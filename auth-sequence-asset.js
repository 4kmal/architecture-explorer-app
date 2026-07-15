(function () {
  'use strict';
  const assets = window.PETAKERJA_DIAGRAM_ASSETS = window.PETAKERJA_DIAGRAM_ASSETS || {};
  const component = (componentKey, nodeIds, uiHotspots, label) => ({ componentKey, id: nodeIds[0], cellIds: [], relationCellIds: [], nodeIds, tableName: null, uiHotspots, label, labelEn: label });
  const connection = (id, sourceComponentKey, targetComponentKey, kind, label) => ({ id, sourceComponentKey, targetComponentKey, kind, label: { ms: label, en: label } });
  assets['auth-sequence'] = {
    svg: { ms: window.PETAKERJA_AUTH_SEQUENCE_SVG || '', en: window.PETAKERJA_AUTH_SEQUENCE_SVG || '' },
    components: [
      component('title', ['auth-manager'], ['user-menu', 'auth-modal'], 'PetaKerja User Login and Logout Sequence'),
      component('user', ['pengguna'], ['user-menu', 'auth-modal'], 'User'),
      component('ui', ['user-menu-manager', 'auth-modal-manager'], ['auth-modal', 'user-menu'], 'PetaKerja UI UserMenuManager / AuthModalManager'),
      component('auth-manager', ['auth-manager'], ['auth-modal', 'user-menu'], 'AuthManager'),
      component('auth-client', ['auth-client'], ['auth-modal', 'user-menu'], 'authClient'),
      component('better-auth', ['better-auth'], ['auth-modal'], 'Better Auth API Express /api/auth/*'),
      component('google-oauth', ['google-oauth'], ['auth-modal'], 'Google OAuth'),
      component('profile-api', ['profile-bridge'], ['user-menu'], 'PetaKerja Profile API /api/me/auth-profile'),
      component('database', ['supabase-db', 'auth-identity', 'user-profile'], ['user-menu'], 'Supabase / PostgreSQL'),
      component('fragment-login-failure', ['auth-modal-manager', 'auth-manager'], ['auth-modal'], 'alt [OAuth]'),
      component('fragment-profile-bridge', ['profile-bridge', 'user-profile'], ['user-menu'], 'alt [profile]'),
      component('fragment-logout-failure', ['auth-manager', 'user-menu-manager'], ['user-menu'], 'alt [sign-out]'),
    ],
    connections: [
      connection('auth-seq-user-ui', 'user', 'ui', 'sequence-sync', 'User action'),
      connection('auth-seq-ui-manager', 'ui', 'auth-manager', 'sequence-sync', 'Authentication action'),
      connection('auth-seq-manager-client', 'auth-manager', 'auth-client', 'sequence-sync', 'Better Auth client call'),
      connection('auth-seq-client-api', 'auth-client', 'better-auth', 'sequence-sync', '/api/auth/*'),
      connection('auth-seq-api-google', 'better-auth', 'google-oauth', 'sequence-async', 'OAuth redirect and callback'),
      connection('auth-seq-manager-profile', 'auth-manager', 'profile-api', 'sequence-sync', '/api/me/auth-profile'),
      connection('auth-seq-profile-api', 'profile-api', 'better-auth', 'sequence-sync', 'Verify Better Auth session'),
      connection('auth-seq-api-db', 'better-auth', 'database', 'sequence-sync', 'Account and session records'),
      connection('auth-seq-profile-db', 'profile-api', 'database', 'sequence-sync', 'Find, link or create public.users'),
      connection('auth-seq-manager-ui', 'auth-manager', 'ui', 'sequence-sync', 'Open prompt or notify subscribers'),
      connection('auth-seq-google-user', 'google-oauth', 'user', 'sequence-sync', 'Account selection and consent'),
      connection('auth-seq-google-api', 'google-oauth', 'better-auth', 'sequence-sync', 'OAuth callback'),
      connection('auth-seq-google-api-error', 'google-oauth', 'better-auth', 'sequence-return', 'OAuth cancellation or error'),
      connection('auth-seq-db-api-return', 'database', 'better-auth', 'sequence-return', 'Session record'),
      connection('auth-seq-api-ui-return', 'better-auth', 'ui', 'sequence-return', 'Redirect and cookie result'),
      connection('auth-seq-api-client-return', 'better-auth', 'auth-client', 'sequence-return', 'Session or sign-out result'),
      connection('auth-seq-api-profile-return', 'better-auth', 'profile-api', 'sequence-return', 'Verified session'),
      connection('auth-seq-db-profile-return', 'database', 'profile-api', 'sequence-return', 'Application profile'),
      connection('auth-seq-profile-self', 'profile-api', 'profile-api', 'sequence-self', 'Profile matching branch'),
      connection('auth-seq-profile-manager-return', 'profile-api', 'auth-manager', 'sequence-return', 'AuthUser profile'),
      connection('auth-seq-manager-self', 'auth-manager', 'auth-manager', 'sequence-self', 'setUser()'),
      connection('auth-seq-client-manager-return', 'auth-client', 'auth-manager', 'sequence-return', 'signOut result'),
      connection('auth-seq-ui-self', 'ui', 'ui', 'sequence-self', 'Render authenticated or guest UI'),
    ],
  };
}());
