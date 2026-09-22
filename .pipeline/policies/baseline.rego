package org.pipeline.governance

# Evaluated against the ReleasePlan, not rendered CI YAML.
# Deny by default; allow only when every rule below is satisfied.
default allow = false

allow {
	approval_for_every_production
	env_gamma_before_prod
	gate_code_review_before_deploy
	gate_load_test_before_env_prod
	gate_security_scan_before_deploy
	gate_unit_test_before_deploy
}

# --- shared helpers ---

provides_class(job, cls) {
	job.classes[_] == cls
}

job_with_id(id) = job {
	some i, j
	input.stages[i].jobs[j].job_id == id
	job := input.stages[i].jobs[j]
}

# --- stage selector helpers ---

stage_env_prod_exists {
	some s
	input.stages[s].environment == "prod"
}

stage_env_prod_at_or_before(i) {
	some s
	input.stages[s].environment == "prod"
	s <= i
}

stage_deploy_exists {
	some s
	input.stages[s].kind == "deploy"
}

stage_deploy_at_or_before(i) {
	some s
	input.stages[s].kind == "deploy"
	s <= i
}

# --- rule helpers ---

# Rule: every production stage must carry an approval
approval_for_every_production {
	not production_without_approval
}

production_without_approval {
	some s
	input.stages[s].is_production
	not approval_named(input.stages[s].name)
}

approval_named(name) {
	input.approvals[_].stage == name
}

# Rule: environment 'gamma' must precede environment 'prod'
env_gamma_before_prod {
	not stage_env_prod_exists
}

env_gamma_before_prod {
	some i
	input.stages[i].environment == "gamma"
	not stage_env_prod_at_or_before(i)
}

# Rule: a passing 'code-review' GATE must precede every deploy stage
gate_code_review_before_deploy {
	not stage_deploy_exists
}

gate_code_review_before_deploy {
	some i, j
	job := input.stages[i].jobs[j]
	job.gate
	provides_class(job, "code-review")
	not stage_deploy_at_or_before(i)
}

# Rule: a passing 'load-test' GATE must precede every 'prod' environment when the change touches services/**
gate_load_test_before_env_prod {
	not stage_env_prod_exists
}

gate_load_test_before_env_prod {
	not touched_load_test_env_prod
}

gate_load_test_before_env_prod {
	some i, j
	job := input.stages[i].jobs[j]
	job.gate
	provides_class(job, "load-test")
	not stage_env_prod_at_or_before(i)
}

touched_load_test_env_prod {
	some k
	glob.match("services/**", ["/"], input.change.files[k])
}

# Rule: a passing 'security-scan' GATE must precede every deploy stage
gate_security_scan_before_deploy {
	not stage_deploy_exists
}

gate_security_scan_before_deploy {
	some i, j
	job := input.stages[i].jobs[j]
	job.gate
	provides_class(job, "security-scan")
	not stage_deploy_at_or_before(i)
}

# Rule: a passing 'unit-test' GATE must precede every deploy stage when the change touches src/**, services/**, lib/**, libs/**
gate_unit_test_before_deploy {
	not stage_deploy_exists
}

gate_unit_test_before_deploy {
	not touched_unit_test_deploy
}

gate_unit_test_before_deploy {
	some i, j
	job := input.stages[i].jobs[j]
	job.gate
	provides_class(job, "unit-test")
	not stage_deploy_at_or_before(i)
}

touched_unit_test_deploy {
	some k
	glob.match("src/**", ["/"], input.change.files[k])
}

touched_unit_test_deploy {
	some k
	glob.match("services/**", ["/"], input.change.files[k])
}

touched_unit_test_deploy {
	some k
	glob.match("lib/**", ["/"], input.change.files[k])
}

touched_unit_test_deploy {
	some k
	glob.match("libs/**", ["/"], input.change.files[k])
}


# --- violation messages ---

deny[msg] {
	not approval_for_every_production
	msg := sprintf("APPROVAL GATE VIOLATION: every production stage requires an approval", [])
}

deny[msg] {
	not env_gamma_before_prod
	msg := sprintf("ENVIRONMENT ORDER VIOLATION: 'gamma' must be released before 'prod'", [])
}

deny[msg] {
	not gate_code_review_before_deploy
	msg := sprintf("ORDERING GATE VIOLATION: a 'code-review' gate must run and pass before any deploy stage", [])
}

deny[msg] {
	not gate_load_test_before_env_prod
	msg := sprintf("ORDERING GATE VIOLATION: the change touches services/**, so a 'load-test' gate must run and pass before any 'prod' environment", [])
}

deny[msg] {
	not gate_security_scan_before_deploy
	msg := sprintf("ORDERING GATE VIOLATION: a 'security-scan' gate must run and pass before any deploy stage", [])
}

deny[msg] {
	not gate_unit_test_before_deploy
	msg := sprintf("ORDERING GATE VIOLATION: the change touches src/**, services/**, lib/**, libs/**, so a 'unit-test' gate must run and pass before any deploy stage", [])
}
