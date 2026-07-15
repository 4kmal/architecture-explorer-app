/**
 * PetaKerja Architecture Explorer integration plugin.
 *
 * This file is an Explorer-specific extension loaded by the locally bundled
 * draw.io runtime. It does not modify the upstream editor implementation.
 */
Draw.loadPlugin(function(editorUi)
{
	var graph = editorUi.editor.graph;
	var parentOrigin = window.location.origin;
	var issueOverlays = [];
	var agentCursor = null;

	function post(message)
	{
		message.source = 'petakerja-explorer-plugin';
		window.parent.postMessage(JSON.stringify(message), parentOrigin);
	}

	function currentPageId()
	{
		return editorUi.currentPage != null ? editorUi.currentPage.getId() : null;
	}

	function postSelection()
	{
		post({
			event: 'petakerja-selection',
			cellIds: graph.getSelectionCells().map(function(cell) { return cell.id; }),
			pageId: currentPageId()
		});
	}

	function clearIssueOverlays()
	{
		for (var i = 0; i < issueOverlays.length; i++)
		{
			graph.removeCellOverlay(issueOverlays[i].cell, issueOverlays[i].overlay);
		}

		issueOverlays = [];
	}

	function issueIcon(severity)
	{
		var fill = severity == 'error' || severity == 'fatal' ? '#a33232' :
			severity == 'warning' ? '#9b6500' : '#356279';
		var glyph = severity == 'error' || severity == 'fatal' ? '!' :
			severity == 'warning' ? '!' : 'i';
		var svg = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18">' +
			'<circle cx="9" cy="9" r="8" fill="' + fill + '" stroke="#fff" stroke-width="1.5"/>' +
			'<text x="9" y="12.2" text-anchor="middle" font-family="Arial" font-size="11" font-weight="700" fill="#fff">' + glyph + '</text></svg>';
		return 'data:image/svg+xml,' + encodeURIComponent(svg);
	}

	function applyIssues(issues)
	{
		clearIssueOverlays();
		var seen = {};

		for (var i = 0; i < issues.length; i++)
		{
			var issue = issues[i];
			var cells = issue.cellIds || [];

			for (var j = 0; j < cells.length; j++)
			{
				var key = cells[j] + ':' + issue.severity;

				if (seen[key])
				{
					continue;
				}

				var cell = graph.model.getCell(cells[j]);

				if (cell != null)
				{
					var label = issue.message || issue.ruleId || 'Diagram validation issue';
					var overlay = new mxCellOverlay(new mxImage(issueIcon(issue.severity), 18, 18), label);
					graph.addCellOverlay(cell, overlay);
					issueOverlays.push({cell: cell, overlay: overlay});
					seen[key] = true;
				}
			}
		}
	}

	function focusCell(cellId)
	{
		var cell = graph.model.getCell(cellId);

		if (cell != null)
		{
			graph.setSelectionCell(cell);
			graph.scrollCellToVisible(cell, true);
			postSelection();
		}
	}

	function focusPage(pageId)
	{
		if (editorUi.pages == null || pageId == null)
		{
			return;
		}

		for (var i = 0; i < editorUi.pages.length; i++)
		{
			if (editorUi.pages[i].getId() == pageId)
			{
				editorUi.selectPage(editorUi.pages[i]);
				postSelection();
				break;
			}
		}
	}

	function ensureAgentCursor()
	{
		if (agentCursor == null)
		{
			agentCursor = document.createElement('div');
			agentCursor.setAttribute('aria-hidden', 'true');
			agentCursor.style.cssText = 'position:absolute;z-index:20;width:18px;height:18px;border:2px solid #12658a;border-radius:50%;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.24);pointer-events:none;transition:left .22s ease,top .22s ease,opacity .15s ease;opacity:0;';
			var dot = document.createElement('span');
			dot.style.cssText = 'position:absolute;left:5px;top:5px;width:6px;height:6px;border-radius:50%;background:#12658a;';
			agentCursor.appendChild(dot);
			graph.container.parentNode.appendChild(agentCursor);
		}
		return agentCursor;
	}

	function showAgentFocus(cell)
	{
		if (cell == null) return;
		graph.setSelectionCell(cell);
		graph.scrollCellToVisible(cell, true);
		var state = graph.view.getState(cell);
		var cursor = ensureAgentCursor();
		if (state != null)
		{
			cursor.style.left = (graph.container.offsetLeft + state.x + Math.max(8, state.width / 2) - 9) + 'px';
			cursor.style.top = (graph.container.offsetTop + state.y + Math.max(8, state.height / 2) - 9) + 'px';
			cursor.style.opacity = '1';
		}
	}

	function findByKey(key)
	{
		var cells = graph.model.cells;
		for (var id in cells)
		{
			if (!Object.prototype.hasOwnProperty.call(cells, id)) continue;
			var cell = cells[id];
			var value = cell.value;
			if (cell.id == key || cell.petakerjaKey == key || (value != null && value.nodeType == 1 && value.getAttribute('petakerjaKey') == key)) return cell;
		}
		return null;
	}

	function cellKey(cell)
	{
		if (cell == null) return null;
		var value = cell.value;
		return cell.petakerjaKey || (value != null && value.nodeType == 1 ? value.getAttribute('petakerjaKey') : null);
	}

	function layoutTargets(parent, keys)
	{
		var targets = Array.isArray(keys) && keys.length > 0 ? keys.map(findByKey) : graph.getChildVertices(parent).filter(function(item)
		{
			return cellKey(item) != null;
		});
		var seen = {};
		return targets.filter(function(item)
		{
			if (item == null || item.edge || seen[item.id]) return false;
			seen[item.id] = true;
			return true;
		});
	}

	function applyCircleLayout(targets)
	{
		if (targets.length == 0) return;
		var bounds = null;
		targets.forEach(function(item)
		{
			var geometry = item.geometry;
			if (geometry == null) return;
			var next = new mxRectangle(geometry.x, geometry.y, geometry.width, geometry.height);
			if (bounds == null) bounds = next;
			else bounds.add(next);
		});
		var centerX = bounds != null ? bounds.x + bounds.width / 2 : 500;
		var centerY = bounds != null ? bounds.y + bounds.height / 2 : 400;
		var radius = Math.max(280, Math.min(900, targets.length * 62));
		targets.forEach(function(item, index)
		{
			var geometry = item.geometry != null ? item.geometry.clone() : new mxGeometry(0, 0, 220, 120);
			var angle = -Math.PI / 2 + (Math.PI * 2 * index / targets.length);
			geometry.x = Math.round(centerX + Math.cos(angle) * radius - geometry.width / 2);
			geometry.y = Math.round(centerY + Math.sin(angle) * radius - geometry.height / 2);
			graph.model.setGeometry(item, geometry);
		});
	}

	function applySequenceLayout(targets)
	{
		var lifelines = targets.filter(function(item)
		{
			return String(item.style || '').indexOf('shape=umlLifeline') >= 0;
		}).sort(function(a, b) { return a.geometry.x - b.geometry.x; });
		var startX = 90;
		var gap = lifelines.length > 7 ? 190 : 220;
		lifelines.forEach(function(item, index)
		{
			var geometry = item.geometry.clone();
			geometry.x = startX + index * gap;
			geometry.y = 70;
			graph.model.setGeometry(item, geometry);
		});
	}

	function componentValue(label, key)
	{
		var doc = mxUtils.createXmlDocument();
		var object = doc.createElement('object');
		// An activation bar intentionally has an empty label.  Falling back to
		// the stable key exposed internal identifiers on the sequence canvas.
		object.setAttribute('label', label != null ? label : (key || 'Component'));
		if (key) object.setAttribute('petakerjaKey', key);
		return object;
	}

	function componentLabel(operation, existingCell)
	{
		if (operation.componentType == 'activation') return '';
		var existing = existingCell != null ? String(graph.convertValueToString(existingCell) || '') : '';
		var existingParts = existing ? existing.split(/<hr\s*\/?\s*>/i) : [];
		var lines = [operation.label || existingParts.shift() || operation.key || 'Component'];
		if (operation.compartments != null)
		{
			var parts = Array.isArray(operation.compartments) ? operation.compartments : Object.values(operation.compartments);
			parts.filter(Boolean).forEach(function(part)
			{
				if (Array.isArray(part)) lines.push(part.join('<br>'));
				else lines.push(String(part));
			});
		}
		else if (existingParts.length) lines = lines.concat(existingParts);
		return lines.join('<hr>');
	}

	function componentStyle(operation)
	{
		var sequenceEdgeStyle = 'newEdgeStyle={"curved":0,"rounded":0};';
		var lifelineStyle = 'shape=umlLifeline;perimeter=lifelinePerimeter;whiteSpace=wrap;html=1;container=1;dropTarget=0;collapsible=0;recursiveResize=0;outlineConnect=0;portConstraint=eastwest;' + sequenceEdgeStyle;
		var activationStyle = 'html=1;points=[[0,0,0,0,5],[0,1,0,0,-5],[1,0,0,0,5],[1,1,0,0,-5]];perimeter=orthogonalPerimeter;outlineConnect=0;targetShapes=umlLifeline;portConstraint=eastwest;' + sequenceEdgeStyle;
		if (operation.stylePreset == 'sequence-title') return 'text;html=1;align=center;verticalAlign=middle;fontSize=22;fontStyle=1;strokeColor=none;fillColor=none;';
		if (operation.componentType == 'actor') return 'shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;html=1;';
		if (operation.componentType == 'usecase') return 'ellipse;whiteSpace=wrap;html=1;';
		if (operation.componentType == 'note') return 'shape=note;whiteSpace=wrap;html=1;';
		if (operation.componentType == 'lifeline')
		{
			var participants = {actor: 'umlActor', boundary: 'umlBoundary', control: 'umlControl', entity: 'umlEntity'};
			return lifelineStyle + (participants[operation.participantType] ? 'participant=' + participants[operation.participantType] + ';' : '');
		}
		if (operation.componentType == 'activation') return activationStyle;
		if (operation.componentType == 'combinedFragment') return 'shape=umlFrame;whiteSpace=wrap;html=1;pointerEvents=0;connectable=0;recursiveResize=0;';
		return 'rounded=0;whiteSpace=wrap;html=1;align=left;verticalAlign=top;spacing=8;';
	}

	function clamp(value, minimum, maximum)
	{
		return Math.max(minimum, Math.min(maximum, value));
	}

	function sequenceTerminalY(cell, absoluteY)
	{
		var geometry = cell != null ? cell.geometry : null;
		if (geometry == null || !geometry.height) return 0.25;
		return clamp((absoluteY - geometry.y) / geometry.height, 0.07, 0.98);
	}

	function relationStyle(kind, operation, source, target)
	{
		if (kind.indexOf('sequence-') == 0)
		{
			var absoluteY = Number(operation.geometry && operation.geometry.y);
			if (!isFinite(absoluteY)) absoluteY = 170;
			var sourceY = sequenceTerminalY(source, absoluteY);
			var targetY = kind == 'sequence-self' ? sequenceTerminalY(target, absoluteY + 34) : sequenceTerminalY(target, absoluteY);
			var anchor = 'exitX=0.5;exitY=' + sourceY + ';exitDx=0;exitDy=0;entryX=0.5;entryY=' + targetY + ';entryDx=0;entryDy=0;';
			if (kind == 'sequence-return') return 'html=1;verticalAlign=bottom;endArrow=open;endFill=0;dashed=1;endSize=8;curved=0;rounded=0;' + anchor;
			if (kind == 'sequence-async') return 'html=1;verticalAlign=bottom;endArrow=open;endFill=0;endSize=8;curved=0;rounded=0;' + anchor;
			if (kind == 'sequence-self') return 'html=1;align=left;spacingLeft=3;endArrow=block;endFill=1;edgeStyle=orthogonalEdgeStyle;curved=0;rounded=0;loopSize=34;' + anchor;
			return 'html=1;verticalAlign=bottom;endArrow=block;endFill=1;curved=0;rounded=0;' + anchor;
		}
		if (kind == 'dependency' || kind == 'include' || kind == 'extend') return 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;endArrow=open;endFill=0;';
		if (kind == 'logical') return 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;dashed=1;endArrow=none;';
		if (kind == 'aggregation') return 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;startArrow=diamond;startFill=0;endArrow=none;';
		if (kind == 'composition') return 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;startArrow=diamond;startFill=1;endArrow=none;';
		return 'edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;endArrow=none;';
	}

	function applyOperation(operation)
	{
		if (operation == null || typeof operation.type != 'string') throw new Error('Invalid diagram operation.');
		if (operation.type == 'createPage')
		{
			var page = editorUi.insertPage();
			if (operation.name) page.setName(operation.name);
			editorUi.selectPage(page);
			editorUi.editor.setModified(true);
			postSelection();
			return {changedCellIds: [], pageId: page.getId()};
		}
		var parent = graph.getDefaultParent();
		var changed = [];
		var cell = null;
		graph.model.beginUpdate();
		try
		{
			if (operation.type == 'createComponent')
			{
				var geometry = operation.geometry || {};
				var style = componentStyle(operation);
				cell = graph.insertVertex(parent, null, componentValue(componentLabel(operation), operation.key), Number(geometry.x) || 40, Number(geometry.y) || 40, Number(geometry.width) || 220, Number(geometry.height) || 120, style);
				changed.push(cell.id);
				if (operation.componentType == 'combinedFragment') graph.orderCells(true, [cell]);
			}
			else if (operation.type == 'updateComponent')
			{
				cell = findByKey(operation.key);
				if (cell == null) throw new Error('Component not found: ' + operation.key);
				graph.model.setValue(cell, componentValue(componentLabel(operation, cell), operation.key));
				if (operation.stylePreset) graph.model.setStyle(cell, componentStyle(operation));
				changed.push(cell.id);
			}
			else if (operation.type == 'moveResize')
			{
				cell = findByKey(operation.key);
				if (cell == null) throw new Error('Component not found: ' + operation.key);
				var next = cell.geometry.clone();
				var update = operation.geometry || {};
				if (update.x != null) next.x = Number(update.x);
				if (update.y != null) next.y = Number(update.y);
				if (update.width != null) next.width = Number(update.width);
				if (update.height != null) next.height = Number(update.height);
				graph.model.setGeometry(cell, next);
				changed.push(cell.id);
			}
			else if (operation.type == 'connect')
			{
				var source = findByKey(operation.sourceKey);
				var target = findByKey(operation.targetKey);
				if (source == null || target == null) throw new Error('Connection endpoint not found.');
				var edgeLabel = operation.label || ((operation.relationKind == 'include' || operation.relationKind == 'extend') ? '&lt;&lt;' + operation.relationKind + '&gt;&gt;' : '');
				cell = graph.insertEdge(parent, null, componentValue(edgeLabel, operation.key), source, target, relationStyle(operation.relationKind, operation, source, target));
				if (operation.relationKind == 'sequence-self' && operation.geometry && isFinite(Number(operation.geometry.y)))
				{
					var selfGeometry = cell.geometry.clone();
					var loopX = source.geometry.x + source.geometry.width + 44;
					selfGeometry.points = [new mxPoint(loopX, Number(operation.geometry.y) + 17)];
					graph.model.setGeometry(cell, selfGeometry);
				}
				changed.push(cell.id);
				if (operation.multiplicities != null)
				{
					var sourceMultiplicity = Array.isArray(operation.multiplicities) ? operation.multiplicities[0] : operation.multiplicities.source;
					var targetMultiplicity = Array.isArray(operation.multiplicities) ? operation.multiplicities[1] : operation.multiplicities.target;
					[[sourceMultiplicity, -0.82], [targetMultiplicity, 0.82]].forEach(function(entry)
					{
						if (entry[0] == null || entry[0] === '') return;
						var labelCell = graph.insertVertex(cell, null, String(entry[0]), entry[1], 0, 48, 20, 'resizable=0;movable=1;connectable=0;html=1;fillColor=none;strokeColor=none;');
						labelCell.geometry.relative = true;
						changed.push(labelCell.id);
					});
				}
			}
			else if (operation.type == 'delete')
			{
				var targets = (operation.keys || []).map(findByKey).filter(function(item) { return item != null; });
				changed = targets.map(function(item) { return item.id; });
				graph.removeCells(targets, true);
			}
			else if (operation.type == 'applyLayout')
			{
				var layoutCells = layoutTargets(parent, operation.keys);
				if (layoutCells.length == 0) throw new Error('No component cells are available for layout.');
				if (operation.algorithm == 'circle') applyCircleLayout(layoutCells);
				else if (operation.algorithm == 'sequence') applySequenceLayout(layoutCells);
				else
				{
					var layout = new mxHierarchicalLayout(graph, mxConstants.DIRECTION_WEST);
					layout.execute(parent, layoutCells);
				}
				changed = layoutCells.map(function(item) { return item.id; });
			}
			else throw new Error('Unsupported diagram operation: ' + operation.type);
		}
		finally
		{
			graph.model.endUpdate();
		}
		if (cell != null) showAgentFocus(cell);
		editorUi.editor.setModified(true);
		postSelection();
		return {changedCellIds: changed, pageId: currentPageId()};
	}

	graph.getSelectionModel().addListener(mxEvent.CHANGE, postSelection);
	editorUi.addListener('currentPageChanged', postSelection);

	window.addEventListener('message', function(event)
	{
		if (event.source != window.parent || event.origin != parentOrigin)
		{
			return;
		}

		var data = event.data;

		if (typeof data == 'string')
		{
			try
			{
				data = JSON.parse(data);
			}
			catch (e)
			{
				return;
			}
		}

		if (data == null)
		{
			return;
		}

		if (data.action == 'petakerja-focus-cell')
		{
			focusCell(data.cellId);
		}
		else if (data.action == 'petakerja-focus-page')
		{
			focusPage(data.pageId);
		}
		else if (data.action == 'petakerja-validation')
		{
			applyIssues(data.issues || []);
		}
		else if (data.action == 'petakerja-commit-edit')
		{
			if (graph.isEditing()) graph.stopEditing(false);
			post({event: 'petakerja-committed'});
		}
		else if (data.action == 'petakerja-prepare-reload')
		{
			if (graph.isEditing()) graph.stopEditing(false);
			post({event: 'petakerja-reload-ready', xml: editorUi.getFileData(true), pageId: currentPageId()});
		}
		else if (data.action == 'petakerja-apply-operation')
		{
			try
			{
				var result = applyOperation(data.operation);
				var response = {event: 'petakerja-operation-result', requestId: data.requestId, ok: true, changedCellIds: result.changedCellIds, pageId: result.pageId, xml: editorUi.getFileData(true)};
				post(response);
			}
			catch (error)
			{
				post({event: 'petakerja-operation-result', requestId: data.requestId, ok: false, error: error.message || String(error)});
			}
		}
	});

	post({event: 'petakerja-ready', pageId: currentPageId()});
});
