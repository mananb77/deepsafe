// Deepfake threat statistics and attack case data

export interface Statistic {
  id: string;
  label: string;
  value: string;
  numericValue: number;
  suffix?: string;
  prefix?: string;
  source: string;
  description: string;
}

export interface AttackCase {
  id: string;
  company: string;
  date: string;
  year: number;
  amount?: string;
  description: string;
  outcome: 'prevented' | 'successful' | 'attempted';
}

export const statistics: Statistic[] = [
  {
    id: 'annual-losses',
    label: 'Annual Losses',
    value: '$25B+',
    numericValue: 25,
    prefix: '$',
    suffix: 'B+',
    source: 'FBI IC3 2024',
    description: 'Annual financial losses from business email compromise and impersonation attacks',
  },
  {
    id: 'attack-growth',
    label: 'Attack Growth',
    value: '3,000%',
    numericValue: 3000,
    suffix: '%',
    source: 'Deloitte 2024',
    description: 'Increase in deepfake-enabled fraud attempts since 2022',
  },
  {
    id: 'detection-rate',
    label: 'Detection Rate',
    value: '<5%',
    numericValue: 5,
    prefix: '<',
    suffix: '%',
    source: 'MIT Media Lab',
    description: 'Human accuracy in detecting high-quality deepfakes without AI assistance',
  },
  {
    id: 'avg-loss',
    label: 'Avg Loss/Incident',
    value: '$680K',
    numericValue: 680,
    prefix: '$',
    suffix: 'K',
    source: 'AICPA Study',
    description: 'Average financial loss per successful deepfake fraud incident',
  },
];

export const attackCases: AttackCase[] = [
  {
    id: 'arup',
    company: 'Arup Engineering',
    date: 'January 2024',
    year: 2024,
    amount: '$25M',
    description: 'Hong Kong finance worker wired $25M after video call with deepfake CFO and colleagues',
    outcome: 'successful',
  },
  {
    id: 'wpp',
    company: 'WPP CEO',
    date: 'May 2024',
    year: 2024,
    description: 'AI voice clone attack attempted against advertising giant using Teams meeting',
    outcome: 'attempted',
  },
  {
    id: 'ferrari',
    company: 'Ferrari',
    date: 'July 2024',
    year: 2024,
    description: 'Deepfake CEO targeted finance executives requesting urgent wire transfer',
    outcome: 'prevented',
  },
  {
    id: 'wiz',
    company: 'Wiz',
    date: 'Late 2024',
    year: 2024,
    description: 'Voice clone voicemails of CEO sent to employees requesting credentials',
    outcome: 'prevented',
  },
];

export const keyInsight = {
  quote: "In video calls, seeing is no longer believing. Traditional security fails when attackers can perfectly replicate faces, voices, and mannerisms in real-time.",
  attribution: null,
};
