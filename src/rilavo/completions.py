"""
Rilavo Shell Completion Generator
Generates completion scripts for bash, zsh, fish, and powershell.
"""

import argparse
import sys
import os
from pathlib import Path


BASH_COMPLETION = """# Rilavo bash completion
_rilavo_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    # Main commands
    local commands="keygen issue smoke explain init conformance doctor service completion"

    # Global options
    local global_opts="--help --version"

    # Subcommand options
    case "${prev}" in
        keygen)
            local opts="--out --help"
            ;;
        issue)
            local opts="--key --principal --agent --agent-pub --action-class --audience --ttl --help"
            ;;
        smoke)
            local opts="--quiet --help"
            ;;
        explain)
            local opts="--help"
            ;;
        init)
            local opts="--framework --dir --target-dir --help"
            ;;
        conformance)
            local opts="--target --help"
            ;;
        doctor)
            local opts="--online --help"
            ;;
        service)
            local opts="--port --metrics-port --metrics-host --otel-endpoint --otel-sampling --help"
            ;;
        completion)
            local opts="bash zsh fish powershell install --help"
            ;;
        *)
            local opts=""
            ;;
    esac

    if [[ ${cur} == -* ]]; then
        COMPREPLY=( $(compgen -W "${global_opts} ${opts}" -- ${cur}) )
    else
        if [[ ${COMP_CWORD} -eq 1 ]]; then
            COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        else
            COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
        fi
    fi

    return 0
}

complete -F _rilavo_completion rilavo
"""


ZSH_COMPLETION = """#compdef rilavo

_rilavo() {
    local -a commands
    local -a global_opts
    local -a keygen_opts
    local -a issue_opts
    local -a smoke_opts
    local -a explain_opts
    local -a init_opts
    local -a conformance_opts
    local -a doctor_opts
    local -a service_opts
    local -a completion_opts

    commands=(
        'keygen:Generate Ed25519 keypair + directory entry'
        'issue:Issue a credential'
        'smoke:End-to-end self-check (issue, verify, reject)'
        'explain:Explain a rejection reason code'
        'init:Scaffold a framework-specific integration'
        'conformance:Mechanical self-check against a target'
        'doctor:Check install health (CLI on PATH, imports, smoke, optional online)'
        'service:Run the rilavo service with metrics endpoint'
        'completion:Generate shell completion scripts'
    )

    global_opts=(
        '--help[Show help message]'
        '--version[Show version]'
    )

    keygen_opts=(
        '--out[Output file for private key]'
        '--help[Show help message]'
    )

    issue_opts=(
        '--key[Issuer private key file]:file:_files'
        '--principal[Principal identifier]'
        '--agent[Agent identifier]'
        '--agent-pub[Agent public key file]:file:_files'
        '--action-class[Action class (e.g., data.read)]'
        '--audience[Audience identifier (e.g., verifier:api.example.com)]'
        '--ttl[TTL in seconds]:integer'
        '--help[Show help message]'
    )

    smoke_opts=(
        '--quiet[Show help message]'
        '--help[Show help message]'
    )

    explain_opts=(
        '--help[Show help message]'
        ':reason_codes:__rilavo_reason_codes'
    )

    init_opts=(
        '--framework[Target framework (fastapi, express, nextjs, go, wordpress)]'
        '--dir:Target directory:_files'
        '--target-dir[Target directory]:file:_files'
        '--help[Show help message]'
    )

    conformance_opts=(
        '--target[Target to test]:string'
        '--help[Show help message]'
    )

    doctor_opts=(
        '--online[Also check online verifier endpoint]'
        '--help[Show help message]'
    )

    service_opts=(
        '--port[Service port]:integer'
        '--metrics-port[Metrics endpoint port]:integer'
        '--metrics-host[Metrics bind address]:string'
        '--otel-endpoint[OTLP endpoint for tracing]:string'
        '--otel-sampling[Trace sampling rate]:float'
        '--help[Show help message]'
    )

    completion_opts=(
        'bash[Generate bash completion]'
        'zsh[Generate zsh completion]'
        'fish[Generate fish completion]'
        'powershell[Generate powershell completion]'
        'install[Install completion for current shell]'
        '--help[Show help message]'
    )

    _arguments -C \\
        ${global_opts} \\
        '1: :->command' \\
        '*::arg:->args'

    case $state in
        command)
            _describe 'command' commands
            ;;
        args)
            case $words[1] in
                keygen)
                    _arguments ${keygen_opts}
                    ;;
                issue)
                    _arguments ${issue_opts}
                    ;;
                smoke)
                    _arguments ${smoke_opts}
                    ;;
                explain)
                    _arguments ${explain_opts}
                    ;;
                init)
                    _arguments ${init_opts}
                    ;;
                conformance)
                    _arguments ${conformance_opts}
                    ;;
                doctor)
                    _arguments ${doctor_opts}
                    ;;
                service)
                    _arguments ${service_opts}
                    ;;
                completion)
                    _arguments ${completion_opts}
                    ;;
            esac
            ;;
    esac
}

# Reason codes for explain command
__rilavo_reason_codes() {
    local -a codes
    codes=(
        'accept:Verification succeeded'
        'unrecognized_version:Credential version not supported'
        'audience_mismatch:Credential audience does not match verifier'
        'expired:Credential has expired'
        'not_yet_valid:Credential not yet valid'
        'unknown_issuer:Issuer not in key directory'
        'key_not_valid_at_issuance:Issuer key expired at credential issuance time'
        'invalid_signature:Credential signature verification failed'
        'replay_detected:Nonce already used'
        'revoked:Credential has been revoked'
        'proof_of_possession_failed:PoP signature verification failed'
        'malformed_credential:Credential JSON parsing failed'
        'no_credentials:No credential header provided'
    )
    _describe 'reason_code' codes
}

_rilavo "$@"
"""


FISH_COMPLETION = """# Rilavo fish completion

function __rilavo_commands
    set -l commands \\
        keygen "Generate Ed25519 keypair + directory entry" \\
        issue "Issue a credential" \\
        smoke "End-to-end self-check (issue, verify, reject)" \\
        explain "Explain a rejection reason code" \\
        init "Scaffold a framework-specific integration" \\
        conformance "Mechanical self-check against a target" \\
        doctor "Check install health" \\
        service "Run the rilavo service with metrics endpoint" \\
        completion "Generate shell completion scripts"
    echo $commands
end

function __rilavo_global_opts
    echo "--help --version"
end

function __rilavo_keygen_opts
    echo "--out --help"
end

function __rilavo_issue_opts
    echo "--key --principal --agent --agent-pub --action-class --audience --ttl --help"
end

function __rilavo_smoke_opts
    echo "--quiet --help"
end

function __rilavo_explain_opts
    echo "--help"
end

function __rilavo_init_opts
    echo "--framework --dir --target-dir --help"
end

function __rilavo_conformance_opts
    echo "--target --help"
end

function __rilavo_doctor_opts
    echo "--online --help"
end

function __rilavo_service_opts
    echo "--port --metrics-port --metrics-host --otel-endpoint --otel-sampling --help"
end

function __rilavo_completion_opts
    echo "bash zsh fish powershell install --help"
end

complete -c rilavo -f -n "__fish_use_subcommand" -a "(__rilavo_commands)"

# Global options
complete -c rilavo -f -n "not __fish_seen_subcommand" -a "(__rilavo_global_opts)"

# Subcommand options
complete -c rilavo -f -n "__fish_seen_subcommand_from keygen" -a "(__rilavo_keygen_opts)"
complete -c rilavo -f -n "__fish_seen_subcommand_from issue" -a "(__rilavo_issue_opts)"
complete -c rilavo -f -n "__fish_seen_subcommand_from smoke" -a "(__rilavo_smoke_opts)"
complete -c rilavo -f -n "__fish_seen_subcommand_from explain" -a "(__rilavo_explain_opts)"
complete -c rilavo -f -n "__fish_seen_subcommand_from init" -a "(__rilavo_init_opts)"
complete -c rilavo -f -n "__fish_seen_subcommand_from conformance" -a "(__rilavo_conformance_opts)"
complete -c rilavo -f -n "__fish_seen_subcommand_from doctor" -a "(__rilavo_doctor_opts)"
complete -c rilavo -f -n "__fish_seen_subcommand_from service" -a "(__rilavo_service_opts)"
complete -c rilavo -f -n "__fish_seen_subcommand_from completion" -a "(__rilavo_completion_opts)"

# Reason codes for explain
function __rilavo_reason_codes
    echo "accept unrecognized_version audience_mismatch expired not_yet_valid unknown_issuer key_not_valid_at_issuance invalid_signature replay_detected revoked proof_of_possession_failed malformed_credential no_credentials"
end

complete -c rilavo -f -n "__fish_seen_subcommand_from explain" -a "(__rilavo_reason_codes)"
"""


POWERSHELL_COMPLETION = """# Rilavo PowerShell completion

Register-ArgumentCompleter -CommandName rilavo -ScriptBlock {
    param($commandName, $wordToComplete, $cursorPosition)

    $commands = @(
        "keygen", "issue", "smoke", "explain", "init", 
        "conformance", "doctor", "service", "completion"
    )

    $globalOpts = @("--help", "--version")

    $subcommandOpts = @{
        "keygen" = @("--out", "--help")
        "issue" = @("--key", "--principal", "--agent", "--agent-pub", "--action-class", "--audience", "--ttl", "--help")
        "smoke" = @("--quiet", "--help")
        "explain" = @("--help", @("accept", "unrecognized_version", "audience_mismatch", "expired", "not_yet_valid", "unknown_issuer", "key_not_valid_at_issuance", "invalid_signature", "replay_detected", "revoked", "proof_of_possession_failed", "malformed_credential", "no_credentials"))
        "init" = @("--framework", "--dir", "--target-dir", "--help")
        "conformance" = @("--target", "--help")
        "doctor" = @("--online", "--help")
        "service" = @("--port", "--metrics-port", "--metrics-host", "--otel-endpoint", "--otel-sampling", "--help")
        "completion" = @("bash", "zsh", "fish", "powershell", "install", "--help")
    }

    $words = $commandName.Split(' ')
    if ($words.Count -eq 1) {
        # No subcommand yet - complete commands and global opts
        $commands + $globalOpts | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object { [System.Management.Automation.CompletionResult]::new($_) }
    } elseif ($words.Count -eq 2) {
        # Completing subcommand
        $commands | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object { [System.Management.Automation.CompletionResult]::new($_) }
    } else {
        # Completing subcommand options
        $subcmd = $words[1]
        if ($subcommandOpts.ContainsKey($subcmd)) {
            $subcommandOpts[$subcmd] | Where-Object { $_ -like "$wordToComplete*" } | ForEach-Object { [System.Management.Automation.CompletionResult]::new($_) }
        }
    }
}
"""


def generate_completion(shell: str) -> str:
    """Generate completion script for the specified shell."""
    templates = {
        "bash": BASH_COMPLETION,
        "zsh": ZSH_COMPLETION,
        "fish": FISH_COMPLETION,
        "powershell": POWERSHELL_COMPLETION,
    }
    return templates.get(shell, "")


def install_completion(shell: str) -> bool:
    """Install completion for the current shell."""
    import os
    script = generate_completion(shell)

    if shell == "bash":
        dest = Path.home() / ".bash_completion.d" / "rilavo"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(BASH_COMPLETION)
        print(f"Installed bash completion to {dest}")
        print("Add to ~/.bashrc: source ~/.bash_completion.d/rilavo")
        return True
    elif shell == "zsh":
        dest = Path.home() / ".zsh" / "completions" / "_rilavo"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(ZSH_COMPLETION)
        print(f"Installed zsh completion to {dest}")
        print("Add to ~/.zshrc: fpath=(~/.zsh/completions $fpath); autoload -Uz compinit && compinit")
        return True
    elif shell == "fish":
        dest = Path.home() / ".config" / "fish" / "completions" / "rilavo.fish"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(FISH_COMPLETION)
        print(f"Installed fish completion to {dest}")
        return True
    elif shell == "powershell":
        profile = Path(os.environ.get("USERPROFILE", "")) / "Documents" / "WindowsPowerShell" / "Microsoft.PowerShell_profile.ps1"
        if not profile.parent.exists():
            profile = Path(os.environ.get("USERPROFILE", "")) / "Documents" / "PowerShell" / "Microsoft.PowerShell_profile.ps1"
        if profile.exists():
            content = profile.read_text()
            if "rilavo" not in content:
                profile.write_text(content + "\n" + POWERSHELL_COMPLETION)
                print(f"Added PowerShell completion to {profile}")
                return True
        print("Could not find PowerShell profile")
        return False
    return False

