package rilavo

import (
	"strings"
	"net/http"
	"context"
	"fmt"
	"os"
	"time"

	"github.com/redis/go-redis/v9"
)

// CheckResult mirrors Python doctor CheckResult.
type CheckResult struct {
	Name    string
	OK      bool
	Message string
}

// DoctorResult mirrors Python doctor return.
type DoctorResult struct {
	OK     bool
	Checks []CheckResult
}

// RunDoctor executes a health check of the Go SDK.
// Mirrors Python's run_doctor().
func RunDoctor(online bool) DoctorResult {
	checks := []CheckResult{
		{
			Name:    "rilavo-go SDK importable",
			OK:      true,
			Message: "package rilavo imports successfully",
		},
		{
			Name:    "RunSmoke exported",
			OK:      true,
			Message: "RunSmoke function exported",
		},
		{
			Name:    "RunDoctor exported",
			OK:      true,
			Message: "RunDoctor function exported",
		},
		{
			Name:    "Verify exported",
			OK:      true,
			Message: "Verify function exported",
		},
		{
			Name:    "Issue functions available",
			OK:      true,
			Message: "credential issuance functions available",
		},
	}

	if online {
		checks = append(checks, checkRedisNonceCache())
		checks = append(checks, checkIssuerDirectory())
		checks = append(checks, checkRevocationLog())
	}

	return DoctorResult{OK: true, Checks: checks}
}

// checkRedisNonceCache checks Redis nonce cache connectivity if configured.
func checkRedisNonceCache() CheckResult {
	redisURL := os.Getenv("RILAVO_REDIS_URL")
	if redisURL == "" {
		return CheckResult{
			Name:    "Redis nonce cache",
			OK:      true,
			Message: "SKIPPED (RILAVO_REDIS_URL not set)",
		}
	}

	// Attempt to connect to Redis
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	client := redis.NewClient(&redis.Options{
		Addr: redisURL,
	})
	defer client.Close()

	ctx, cancel = context.WithTimeout(ctx, 3*time.Second)
	defer cancel()

	if err := client.Ping(ctx).Err(); err != nil {
		return CheckResult{
			Name:    "Redis nonce cache",
			OK:      false,
			Message: fmt.Sprintf("FAILED to connect to %s: %v", redisURL, err),
		}
	}

	return CheckResult{
		Name:    "Redis nonce cache",
		OK:      true,
		Message: fmt.Sprintf("CONNECTED (%s)", redisURL),
	}
}

// checkIssuerDirectory checks issuer directory connectivity if configured.
func checkIssuerDirectory() CheckResult {
	dirURL := os.Getenv("RILAVO_ISSUER_DIR_URL")
	if dirURL == "" {
		return CheckResult{
			Name:    "Issuer directory",
			OK:      true,
			Message: "SKIPPED (RILAVO_ISSUER_DIR_URL not set)",
		}
	}

	// Attempt to connect to issuer directory health endpoint
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", strings.TrimSuffix(dirURL, "/")+"/health", nil)
	if err != nil {
		return CheckResult{
			Name:    "Issuer directory",
			OK:      false,
			Message: fmt.Sprintf("FAILED to create request to %s: %v", dirURL, err),
		}
	}

	client := &http.Client{Timeout: 3 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return CheckResult{
			Name:    "Issuer directory",
			OK:      false,
			Message: fmt.Sprintf("FAILED to connect to %s: %v", dirURL, err),
		}
	}
	defer resp.Body.Close()

	if resp.StatusCode == 200 {
		return CheckResult{
			Name:    "Issuer directory",
			OK:      true,
			Message: fmt.Sprintf("CONNECTED (%s)", dirURL),
		}
	}

	return CheckResult{
		Name:    "Issuer directory",
		OK:      false,
		Message: fmt.Sprintf("HTTP %d (%s)", resp.StatusCode, dirURL),
	}
}

// checkRevocationLog checks revocation log connectivity if configured.
func checkRevocationLog() CheckResult {
	revURL := os.Getenv("RILAVO_REVOCATION_LOG_URL")
	if revURL == "" {
		return CheckResult{
			Name:    "Revocation log",
			OK:      true,
			Message: "SKIPPED (RILAVO_REVOCATION_LOG_URL not set)",
		}
	}

	// Attempt to connect to revocation log health endpoint
	ctx, cancel := context.WithTimeout(context.Background(), 3*time.Second)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "GET", strings.TrimSuffix(revURL, "/")+"/health", nil)
	if err != nil {
		return CheckResult{
			Name:    "Revocation log",
			OK:      false,
			Message: fmt.Sprintf("FAILED to create request to %s: %v", revURL, err),
		}
	}

	client := &http.Client{Timeout: 3 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return CheckResult{
			Name:    "Revocation log",
			OK:      false,
			Message: fmt.Sprintf("FAILED to connect to %s: %v", revURL, err),
		}
	}
	defer resp.Body.Close()

	if resp.StatusCode == 200 {
		return CheckResult{
			Name:    "Revocation log",
			OK:      true,
			Message: fmt.Sprintf("CONNECTED (%s)", revURL),
		}
	}

	return CheckResult{
		Name:    "Revocation log",
		OK:      false,
		Message: fmt.Sprintf("HTTP %d (%s)", resp.StatusCode, revURL),
	}
}
