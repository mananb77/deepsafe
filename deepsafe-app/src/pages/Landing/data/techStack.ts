// Technology stack information

export interface Technology {
  name: string;
  version?: string;
  purpose: string;
  category: 'frontend' | 'backend' | 'ai' | 'infrastructure';
  icon?: string;
}

export const frontendStack: Technology[] = [
  { name: 'React', version: '19.2.0', purpose: 'UI Framework', category: 'frontend' },
  { name: 'TypeScript', version: '5.x', purpose: 'Type Safety', category: 'frontend' },
  { name: 'Material-UI', version: '7.3.6', purpose: 'Component Library', category: 'frontend' },
  { name: 'Vite', version: '6.x', purpose: 'Build Tooling', category: 'frontend' },
  { name: 'Framer Motion', version: '12.x', purpose: 'Animations', category: 'frontend' },
  { name: 'React Router', version: '7.10.1', purpose: 'Navigation', category: 'frontend' },
  { name: 'React Query', version: '5.90.12', purpose: 'Data Fetching', category: 'frontend' },
];

export const backendStack: Technology[] = [
  { name: 'FastAPI', purpose: 'API Framework', category: 'backend' },
  { name: 'PostgreSQL', purpose: 'Database', category: 'backend' },
  { name: 'SQLAlchemy', version: '2.0', purpose: 'ORM', category: 'backend' },
  { name: 'WebSocket', purpose: 'Real-time Updates', category: 'backend' },
  { name: 'JWT', purpose: 'Authentication', category: 'backend' },
  { name: 'Redis', purpose: 'Caching & Sessions', category: 'backend' },
];

export const aiStack: Technology[] = [
  { name: 'TensorFlow', purpose: 'Deepfake Detection', category: 'ai' },
  { name: 'OpenCV', purpose: 'Video Processing', category: 'ai' },
  { name: 'librosa', purpose: 'Audio Analysis', category: 'ai' },
  { name: 'scikit-learn', purpose: 'Behavioral Models', category: 'ai' },
  { name: 'PyTorch', purpose: 'Neural Networks', category: 'ai' },
];

export const infrastructureStack: Technology[] = [
  { name: 'Docker', purpose: 'Containerization', category: 'infrastructure' },
  { name: 'Kubernetes', purpose: 'Orchestration', category: 'infrastructure' },
  { name: 'GitHub Actions', purpose: 'CI/CD', category: 'infrastructure' },
  { name: 'AWS', purpose: 'Cloud Platform', category: 'infrastructure' },
];

export const projectStructure = `
deepsafe-app/
├── src/
│   ├── components/     # Reusable UI components
│   ├── pages/          # Page-level components
│   ├── context/        # React context providers
│   ├── theme/          # Design system
│   ├── data/           # Mock data
│   ├── types/          # TypeScript types
│   ├── hooks/          # Custom React hooks
│   └── services/       # API services
├── public/             # Static assets
├── .github/            # GitHub Actions
└── docs/               # Documentation
`;

export const installationSteps = [
  {
    step: 1,
    command: 'git clone https://github.com/mananb77/deepsafe.git',
    description: 'Clone the repository',
  },
  {
    step: 2,
    command: 'cd deepsafe-app && npm install',
    description: 'Install dependencies',
  },
  {
    step: 3,
    command: 'npm run dev',
    description: 'Start development server',
  },
  {
    step: 4,
    command: 'npm run build',
    description: 'Build for production',
  },
];
