export interface WorkflowFormData {
  query: string;
  owner: string;
  repo: string;
}

export interface WorkflowResult {
  success: boolean;
  message: string;
  confluencePages: Array<{
    title: string;
    message: string;
  }>;
  githubIssues: Array<{
    issueNumber: number;
    issueUrl: string;
    title: string;
  }>;
  steps: Array<{
    stepId: string;
    status?: 'success' | 'error';
  }>;
  error?: string;
}