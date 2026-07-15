const D = 'auth-sequence';
const key = (value) => `${D}/${value}`;
const component = (name, componentType, label, geometry, extra = {}) => ({ type: 'createComponent', key: key(name), componentType, label, geometry, ...extra });
const message = (number, source, target, relationKind, label, y) => ({
  type: 'connect', key: key(`message-${String(number).padStart(2, '0')}`),
  sourceKey: key(source), targetKey: key(target), relationKind, label, geometry: { y },
});

const operations = [
  component('title', 'class', 'PetaKerja User Login and Logout Sequence', { x: 520, y: 18, width: 1120, height: 42 }, { stylePreset: 'sequence-title' }),

  component('fragment-login-failure', 'combinedFragment', 'alt [OAuth]', { x: 210, y: 332, width: 1830, height: 340 }),
  component('fragment-profile-bridge', 'combinedFragment', 'alt [profile]', { x: 1450, y: 925, width: 590, height: 215 }),
  component('fragment-logout-failure', 'combinedFragment', 'alt [sign-out]', { x: 210, y: 1250, width: 1830, height: 475 }),

  component('user', 'lifeline', 'User', { x: 60, y: 82, width: 80, height: 1640 }, { participantType: 'actor' }),
  component('ui', 'lifeline', 'PetaKerja UI<br><span style="font-size:8px">UserMenuManager / AuthModalManager</span>', { x: 220, y: 82, width: 240, height: 1640 }, { participantType: 'boundary' }),
  component('auth-manager', 'lifeline', 'AuthManager', { x: 520, y: 82, width: 150, height: 1640 }, { participantType: 'control' }),
  component('auth-client', 'lifeline', 'authClient', { x: 760, y: 82, width: 140, height: 1640 }, { participantType: 'object' }),
  component('better-auth', 'lifeline', 'Better Auth API<br><span style="font-size:9px">Express /api/auth/*</span>', { x: 980, y: 82, width: 190, height: 1640 }, { participantType: 'control' }),
  component('google-oauth', 'lifeline', 'Google OAuth', { x: 1260, y: 82, width: 150, height: 1640 }, { participantType: 'boundary' }),
  component('profile-api', 'lifeline', 'PetaKerja Profile API<br><span style="font-size:9px">/api/me/auth-profile</span>', { x: 1470, y: 82, width: 220, height: 1640 }, { participantType: 'control' }),
  component('database', 'lifeline', 'Supabase / PostgreSQL', { x: 1790, y: 82, width: 200, height: 1640 }, { participantType: 'entity' }),

  component('activation-ui-login', 'activation', '', { x: 334, y: 158, width: 12, height: 530 }),
  component('activation-auth-login', 'activation', '', { x: 589, y: 194, width: 12, height: 448 }),
  component('activation-client-login', 'activation', '', { x: 824, y: 340, width: 12, height: 270 }),
  component('activation-api-login', 'activation', '', { x: 1074, y: 378, width: 12, height: 235 }),
  component('activation-google', 'activation', '', { x: 1329, y: 412, width: 12, height: 188 }),
  component('activation-auth-init', 'activation', '', { x: 589, y: 694, width: 12, height: 555 }),
  component('activation-client-session', 'activation', '', { x: 824, y: 728, width: 12, height: 112 }),
  component('activation-api-session', 'activation', '', { x: 1074, y: 760, width: 12, height: 130 }),
  component('activation-profile', 'activation', '', { x: 1579, y: 826, width: 12, height: 380 }),
  component('activation-db-profile', 'activation', '', { x: 1889, y: 942, width: 12, height: 185 }),
  component('activation-ui-logout', 'activation', '', { x: 334, y: 1260, width: 12, height: 425 }),
  component('activation-auth-logout', 'activation', '', { x: 589, y: 1295, width: 12, height: 365 }),
  component('activation-client-logout', 'activation', '', { x: 824, y: 1330, width: 12, height: 285 }),
  component('activation-api-logout', 'activation', '', { x: 1074, y: 1365, width: 12, height: 175 }),
  component('activation-db-logout', 'activation', '', { x: 1889, y: 1400, width: 12, height: 70 }),

  message(1, 'user', 'ui', 'sequence-sync', '1. Select Sign in', 170),
  message(2, 'ui', 'auth-manager', 'sequence-sync', '2. requireAuth()', 205),
  message(3, 'auth-manager', 'ui', 'sequence-sync', '3. openAuthPrompt()', 240),
  message(4, 'user', 'ui', 'sequence-sync', '4. Select Google', 278),
  message(5, 'ui', 'auth-manager', 'sequence-sync', '5. signInWithOAuth("google")', 314),
  message(6, 'auth-manager', 'auth-client', 'sequence-sync', '6. signIn.social({ provider: "google" })', 350),
  message(7, 'auth-client', 'better-auth', 'sequence-sync', '7. POST /api/auth/sign-in/social', 386),
  message(8, 'better-auth', 'google-oauth', 'sequence-async', '8. Redirect to Google OAuth', 422),
  message(9, 'google-oauth', 'user', 'sequence-sync', '9. Account selection / consent', 458),
  message(10, 'google-oauth', 'better-auth', 'sequence-sync', '10. GET /api/auth/callback/google', 494),
  message(11, 'better-auth', 'database', 'sequence-sync', '11. Create or update account and session', 530),
  message(12, 'database', 'better-auth', 'sequence-return', 'Account + session persisted', 566),
  message(13, 'better-auth', 'ui', 'sequence-return', '12. Set session cookie; redirect to PetaKerja', 602),
  message(14, 'google-oauth', 'better-auth', 'sequence-return', '[else] OAuth error or cancellation', 632),
  message(15, 'better-auth', 'ui', 'sequence-return', 'Redirect without an authenticated session', 660),

  message(16, 'ui', 'auth-manager', 'sequence-sync', '13. init()', 704),
  message(17, 'auth-manager', 'auth-client', 'sequence-sync', '14. getSession()', 738),
  message(18, 'auth-client', 'better-auth', 'sequence-sync', '15. GET /api/auth/get-session', 772),
  message(19, 'better-auth', 'auth-client', 'sequence-return', 'Better Auth session', 806),
  message(20, 'auth-manager', 'profile-api', 'sequence-sync', '16. GET /api/me/auth-profile', 840),
  message(21, 'profile-api', 'better-auth', 'sequence-sync', '17. getAppSessionFromHeaders()', 874),
  message(22, 'better-auth', 'profile-api', 'sequence-return', 'Verified Better Auth session', 908),
  message(23, 'profile-api', 'database', 'sequence-sync', '18. Find users by better_auth_user_id', 954),
  message(24, 'database', 'profile-api', 'sequence-return', '[found] public.users row', 988),
  message(25, 'profile-api', 'profile-api', 'sequence-self', '[not linked] Find existing user by email', 1022),
  message(26, 'profile-api', 'database', 'sequence-sync', '[email match] Link better_auth_user_id', 1062),
  message(27, 'profile-api', 'database', 'sequence-sync', '[no match] INSERT public.users', 1096),
  message(28, 'database', 'profile-api', 'sequence-return', 'Application profile', 1130),
  message(29, 'profile-api', 'auth-manager', 'sequence-return', 'AuthUser profile', 1165),
  message(30, 'auth-manager', 'auth-manager', 'sequence-self', '19. setUser(profile)', 1200),
  message(31, 'auth-manager', 'ui', 'sequence-sync', '20. Notify subscribers; render authenticated menu', 1232),

  message(32, 'user', 'ui', 'sequence-sync', '21. Select Sign Out', 1270),
  message(33, 'ui', 'auth-manager', 'sequence-sync', '22. handleSignOut() calls signOut()', 1305),
  message(34, 'auth-manager', 'auth-client', 'sequence-sync', '23. signOut()', 1340),
  message(35, 'auth-client', 'better-auth', 'sequence-sync', '24. POST /api/auth/sign-out', 1375),
  message(36, 'better-auth', 'database', 'sequence-sync', '25. Invalidate Better Auth session', 1410),
  message(37, 'database', 'better-auth', 'sequence-return', 'Session invalidated', 1445),
  message(38, 'better-auth', 'auth-client', 'sequence-return', 'Clear session cookie', 1480),
  message(39, 'auth-client', 'auth-manager', 'sequence-return', 'signOut() resolved', 1515),
  message(40, 'auth-manager', 'auth-manager', 'sequence-self', '26. setUser(null)', 1550),
  message(41, 'auth-manager', 'ui', 'sequence-sync', '27. Notify subscribers', 1585),
  message(42, 'ui', 'ui', 'sequence-self', '28. Close authenticated views; render guest sign-in', 1620),
  message(43, 'better-auth', 'auth-client', 'sequence-return', '[else] Sign-out error response', 1660),
  message(44, 'auth-client', 'auth-manager', 'sequence-return', 'Reject signOut(); keep current session state', 1695),
];

export const authSequencePlan = {
  id: 'petakerja-auth-sequence-20260714',
  title: 'PetaKerja User Login and Logout Sequence',
  diagramType: D,
  summary: 'Creates a fresh English UML sequence diagram from the current UserMenuManager, AuthModalManager, AuthManager, Better Auth and public.users profile-bridge flow.',
  warnings: ['Google OAuth only; no unsupported password authentication is shown.', 'The profile alternatives are mutually exclusive even though all guarded messages remain visible for documentation.'],
  operations,
};

export default authSequencePlan;
