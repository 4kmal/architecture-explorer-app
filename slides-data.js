(function () {
  'use strict';

  const t = (en, ms) => ({ en, ms });

  window.PETAKERJA_SLIDES = Object.freeze({
    schemaVersion: 1,
    defaultLanguage: 'ms',
    defaultTheme: 'ukm-neutral',
    aspectRatio: '16:9',
    presets: [{
      id: 'ukm-fyp-2026',
      title: t('UKM FYP Presentation 2026', 'Pembentangan FYP UKM 2026'),
      description: t(
        'A 12-slide guided deck aligned with the UKM submission and presentation guide.',
        'Dek berpandukan 12 slaid yang diselaraskan dengan garis panduan penyerahan dan pembentangan UKM.',
      ),
      targetSeconds: 555,
      slides: [
        { key: 'title', durationSeconds: 10, title: t('PetaKerja', 'PetaKerja'), subtitle: t('Malaysia Job Discovery and Spatial Intelligence Platform', 'Platform Penemuan Pekerjaan dan Kecerdasan Ruang Malaysia'), section: 'title' },
        { key: 'problem', durationSeconds: 50, title: t('Problem, objectives and scope', 'Masalah, objektif dan skop'), subtitle: t('Why PetaKerja is needed and what the project covers', 'Mengapa PetaKerja diperlukan dan skop projek'), section: 'problem' },
        { key: 'overview', durationSeconds: 45, title: t('System overview and proposed solution', 'Gambaran sistem dan cadangan penyelesaian'), subtitle: t('One workspace connecting location, work and open data', 'Satu ruang kerja yang menghubungkan lokasi, pekerjaan dan data terbuka'), section: 'solution' },
        { key: 'architecture', durationSeconds: 55, title: t('Architecture and development approach', 'Seni bina dan pendekatan pembangunan'), subtitle: t('Vite, Express, Supabase, Better Auth and external services', 'Vite, Express, Supabase, Better Auth dan perkhidmatan luar'), section: 'methodology' },
        { key: 'map', durationSeconds: 40, title: t('Malaysia map, POI and open data', 'Peta Malaysia, POI dan data terbuka'), subtitle: t('Spatial exploration and contextual analytics', 'Penerokaan ruang dan analitik berkonteks'), section: 'features' },
        { key: 'jobs', durationSeconds: 40, title: t('Job discovery and application status', 'Penemuan pekerjaan dan status permohonan'), subtitle: t('Search, inspect and organise job opportunities', 'Cari, lihat dan susun peluang pekerjaan'), section: 'features' },
        { key: 'ai-admin', durationSeconds: 40, title: t('AI assistant and administration', 'Pembantu AI dan pentadbiran'), subtitle: t('Contextual assistance, usage visibility and controls', 'Bantuan berkonteks, pemantauan penggunaan dan kawalan'), section: 'features' },
        { key: 'demo-intro', durationSeconds: 40, title: t('Prototype demonstration', 'Demonstrasi prototaip'), subtitle: t('What will be shown and the scenario used', 'Perkara yang akan ditunjukkan dan senario demonstrasi'), section: 'demo' },
        { key: 'demo-flow', durationSeconds: 55, title: t('Main user-flow demonstration', 'Demonstrasi aliran pengguna utama'), subtitle: t('From map context to a relevant job opportunity', 'Daripada konteks peta kepada peluang pekerjaan yang relevan'), section: 'demo' },
        { key: 'testing', durationSeconds: 75, title: t('Testing approach and results', 'Pendekatan dan hasil pengujian'), subtitle: t('Functional coverage, usability checks and known limits', 'Liputan fungsi, semakan kebolehgunaan dan batasan yang diketahui'), section: 'testing' },
        { key: 'value', durationSeconds: 60, title: t('Entrepreneurial value and project potential', 'Nilai keusahawanan dan potensi projek'), subtitle: t('Users, partners, differentiation and future direction', 'Pengguna, rakan kerjasama, perbezaan dan hala tuju masa depan'), section: 'value' },
        { key: 'conclusion', durationSeconds: 45, title: t('Conclusion and Q&A', 'Kesimpulan dan soal jawab'), subtitle: t('PetaKerja brings job discovery into geographic context', 'PetaKerja membawa penemuan pekerjaan ke dalam konteks geografi'), section: 'conclusion' },
      ],
    }],
    themes: [{
      id: 'ukm-neutral',
      title: t('UKM Neutral', 'UKM Neutral'),
      light: { background: '#f8fafc', surface: '#ffffff', text: '#17212b', muted: '#5f6d7a', primary: '#173f5f', secondary: '#d9e5ee', border: '#c9d3dc' },
      dark: { background: '#10161d', surface: '#18212b', text: '#eef4f8', muted: '#a8b4bf', primary: '#7bb9dd', secondary: '#273b4a', border: '#405160' },
    }],
    requiredSections: ['problem', 'methodology', 'solution', 'features', 'demo', 'testing', 'value', 'conclusion'],
    sectionLabels: {
      problem: t('Problem and objectives', 'Masalah dan objektif'),
      methodology: t('Methodology and development', 'Metodologi dan pembangunan'),
      solution: t('Proposed solution', 'Cadangan penyelesaian'),
      features: t('Core features', 'Fungsi teras'),
      demo: t('Prototype demonstration', 'Demonstrasi prototaip'),
      testing: t('Testing and results', 'Pengujian dan hasil'),
      value: t('Entrepreneurial value', 'Nilai keusahawanan'),
      conclusion: t('Conclusion', 'Kesimpulan'),
    },
  });
}());
