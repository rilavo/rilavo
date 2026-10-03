/** /**
 * Doctor/health check for TypeScript SDK - mirrors Python run_doctor() conceptually.
 * This is a structural check - verifies API surface exists.
 */
export interface CheckResult {
    name: string;
    ok: boolean;
    message: string;
}
export interface DoctorResult {
    ok: boolean;
    checks: CheckResult[];
}
export declare function runDoctor(online?: boolean): Promise<{
    ok: boolean;
    checks: CheckResult[];
}>;
export interface DoctorOptions {
    online?: boolean;
}
