export interface Project {
  id: string;
  name: string;
  description?: string;
  created_at: string;
}

export interface Application {
  id: string;
  project_id: string;
  name: string;
  base_url: string;
  description?: string;
  default_environment: string;
  auth_type: string;
  created_at: string;
}

export interface TestStep {
  step_number: number;
  action: string;
  target_description: string;
  selector?: string;
  value?: string;
  expected?: string;
}

export interface TestCase {
  id: string;
  application_id: string;
  test_suite_id?: string;
  custom_id: string;
  module: string;
  feature: string;
  scenario: string;
  preconditions?: string;
  test_data?: Record<string, any>;
  steps: TestStep[];
  expected_result: string;
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  test_type: string;
  tags: string[];
  is_enabled: boolean;
  created_at: string;
}

export interface TestSuite {
  id: string;
  project_id: string;
  name: string;
  description?: string;
  suite_type: string;
  created_at: string;
}

export interface StepExecutionResult {
  step_number: number;
  action: string;
  target: string;
  status: 'SUCCESS' | 'FAILED' | 'BLOCKED' | 'SKIPPED' | 'RETRIED';
  duration_ms: number;
  error?: string;
  recovered_selector?: string;
  screenshot_path?: string;
}

export interface TestResult {
  id: string;
  test_case_id: string;
  status: 'PASS' | 'FAIL' | 'BLOCKED' | 'INCONCLUSIVE';
  confidence: number;
  expected_result?: string;
  actual_result?: string;
  error_message?: string;
  failure_category?: string;
  execution_duration_ms: number;
  retries_used: number;
  step_results: StepExecutionResult[];
  screenshot_path?: string;
  created_at: string;
}

export interface Bug {
  id: string;
  custom_id: string;
  test_run_id: string;
  title: string;
  module: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  priority: 'Critical' | 'High' | 'Medium' | 'Low';
  category: string;
  environment: string;
  application_url: string;
  steps_to_reproduce: string[];
  expected_result: string;
  actual_result: string;
  root_cause_hypothesis: string;
  severity_reasoning: string;
  evidence: {
    screenshot?: string;
    network_errors?: any[];
    console_errors?: any[];
  };
  status: 'OPEN' | 'FALSE_POSITIVE' | 'RESOLVED';
  created_at: string;
}

export interface TestRun {
  id: string;
  application_id: string;
  test_suite_id?: string;
  name: string;
  status: 'PENDING' | 'RUNNING' | 'PAUSED' | 'COMPLETED' | 'STOPPED' | 'FAILED';
  mode: 'SMOKE' | 'FUNCTIONAL' | 'REGRESSION' | 'UI' | 'NEGATIVE' | 'EXPLORATORY' | 'FULL_QA';
  environment: string;
  browser: string;
  headless: boolean;
  total_tests: number;
  passed_tests: number;
  failed_tests: number;
  blocked_tests: number;
  inconclusive_tests: number;
  pass_percentage: number;
  duration_seconds: number;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  summary_report?: any;
}

export interface ExecutionLog {
  id: string;
  test_run_id: string;
  test_id?: string;
  agent: string;
  action: string;
  target: string;
  result: string;
  duration_ms: number;
  error?: string;
  log_metadata?: Record<string, any>;
  created_at: string;
}

export interface AgentSettings {
  llm_provider: string;
  openai_configured: boolean;
  openai_api_key?: string;
  openai_base_url: string;
  openai_model: string;
  ollama_base_url: string;
  ollama_model: string;
  default_browser: string;
  headless: boolean;
  confidence_threshold: number;
  max_retries: number;
}
