/**
 * Smoke test that verifies the SDK's core API surface works.
 * This is a structural test - the actual crypto is tested in index.test.ts
 * This just verifies the API surface exists and returns expected structure.
 */
export declare function runSmoke(): {
    ok: boolean;
    steps: string[];
};
export interface SmokeResult {
    ok: boolean;
    steps: string[];
}
