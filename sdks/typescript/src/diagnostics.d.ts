/**
 * Developer-UX diagnostics: human-readable explanations for every
 * verification rejection reason code. Parity with Python diagnostics.py.
 */
export interface Explanation {
    summary: string;
    likely_causes: string[];
    remediation: string[];
    doc_pointer: string;
}
export declare const EXPLANATIONS: Record<string, Explanation>;
export declare function explainRejection(code: string): Explanation;
export declare function formatExplanation(explanation: Explanation): string;
