#!/usr/bin/env bats

missing_vars=()

require_var() {
  [[ "${!1}" ]] || missing_vars+=("$1")
}

require_var MKWHEELHOUSE_BUCKET_STANDARD
require_var MKWHEELHOUSE_BUCKET_NONSTANDARD

if [[ ${#missing_vars[*]} -gt 0 ]]; then
  echo "Missing required environment variables:"
  printf '    %s\n' "${missing_vars[@]}"
  exit 1
fi

setup() {
  pip uninstall --yes jinja2 pytsdb zini &> /dev/null || true
}

assert_not_found() {
  [[ "$output" == *"No distributions at all found for $1"* || "$output" == *"No matching distribution found for $1"* ]]
}

@test "standard: packages only" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_STANDARD" jinja2
}

@test "standard: -r only" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_STANDARD" \
    -r "$BATS_TEST_DIRNAME/requirements/default.txt"
}

@test "standard: --requirement only" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_STANDARD" \
    --requirement "$BATS_TEST_DIRNAME/requirements/default.txt"
}

@test "standard: --requirement and package" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_STANDARD" \
    --requirement "$BATS_TEST_DIRNAME/requirements/default.txt"
}

@test "standard: -e" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_STANDARD" \
    --requirement "$BATS_TEST_DIRNAME/requirements/exclusions.txt" \
    -e unittest2-1.0.1-py2.py3-none-any.whl
}

@test "standard: --exclude" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_STANDARD" \
    --requirement "$BATS_TEST_DIRNAME/requirements/exclusions.txt" \
    --exclude unittest2-1.0.1-py2.py3-none-any.whl
}

@test "standard: install with acl private (default)" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_STANDARD-private" jinja2
}

@test "standard: no bucket specified" {
  run mkwheelhouse
  [[ "$status" -eq 2 ]]
  [[ "$output" == *"too few arguments"* || $output == *"the following arguments are required: bucket"* ]]
}

@test "standard: no package or requirement specified" {
  run mkwheelhouse "$MKWHEELHOUSE_BUCKET_STANDARD"
  [[ "$status" -eq 2 ]]
  [[ "$output" == *"specify at least one requirements file or package"* ]]
}

@test "standard: pip can't install excluded packages" {
  run pip install \
    --no-index \
    --find-links "https://s3.amazonaws.com/$MKWHEELHOUSE_BUCKET_STANDARD/index.html" \
    unittest2
  [[ "$status" -eq 1 ]]
  assert_not_found unittest2
}

@test "standard: pip can install built packages" {
  pip install \
    --no-index \
    --find-links "https://s3.amazonaws.com/$MKWHEELHOUSE_BUCKET_STANDARD/index.html" \
    jinja2 pytsdb
}

@test "standard: mkwheelhouse builds into prefix" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_STANDARD/deep/rooted/fear" zini
}

@test "standard: pip can install built packages in prefix" {
  pip install \
    --no-index \
    --find-links "https://s3.amazonaws.com/$MKWHEELHOUSE_BUCKET_STANDARD/deep/rooted/fear/index.html" \
    zini
}

@test "standard: pip can't install non-prefixed packages from prefix" {
  run pip install \
    --no-index \
    --find-links "https://s3.amazonaws.com/$MKWHEELHOUSE_BUCKET_STANDARD/deep/rooted/fear/index.html" \
    jinja2
  [[ "$status" -eq 1 ]]
  assert_not_found jinja2
}

@test "standard: pip can't install packages from acl private" {
  run pip install \
    --no-index \
    --find-links "https://s3.amazonaws.com/$MKWHEELHOUSE_BUCKET_STANDARD-private/index.html" \
    jinja2
  [[ "$status" -eq 1 ]]
  assert_not_found jinja2
}

@test "standard: install with acl public-read" {
  mkwheelhouse --acl public-read "$MKWHEELHOUSE_BUCKET_STANDARD-private" jinja2
}

@test "standard: pip can install packages from acl public-read" {
  pip install \
    --no-index \
    --find-links "https://s3.amazonaws.com/$MKWHEELHOUSE_BUCKET_STANDARD-private/index.html" \
    jinja2
}

@test "nonstandard: packages only" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_NONSTANDARD" jinja2
}

@test "nonstandard: -r only" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_NONSTANDARD" \
    -r "$BATS_TEST_DIRNAME/requirements/default.txt"
}

@test "nonstandard: --requirement only" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_NONSTANDARD" \
    --requirement "$BATS_TEST_DIRNAME/requirements/default.txt"
}

@test "nonstandard: --requirement and package" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_NONSTANDARD" \
    --requirement "$BATS_TEST_DIRNAME/requirements/default.txt"
}

@test "nonstandard: -e" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_NONSTANDARD" \
    --requirement "$BATS_TEST_DIRNAME/requirements/exclusions.txt" \
    -e unittest2-1.0.1-py2.py3-none-any.whl
}

@test "nonstandard: --exclude" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_NONSTANDARD" \
    --requirement "$BATS_TEST_DIRNAME/requirements/exclusions.txt" \
    --exclude unittest2-1.0.1-py2.py3-none-any.whl
}

@test "nonstandard: install with acl private (default)" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_NONSTANDARD-private" jinja2
}

@test "nonstandard: no bucket specified" {
  run mkwheelhouse
  [[ "$status" -eq 2 ]]
  [[ "$output" == *"too few arguments"* || $output == *"the following arguments are required: bucket"* ]]
}

@test "nonstandard: no package or requirement specified" {
  run mkwheelhouse "$MKWHEELHOUSE_BUCKET_NONSTANDARD"
  [[ "$status" -eq 2 ]]
  [[ "$output" == *"specify at least one requirements file or package"* ]]
}

@test "nonstandard: pip can't install excluded packages" {
  run pip install \
    --no-index \
    --find-links "https://s3-eu-west-1.amazonaws.com/$MKWHEELHOUSE_BUCKET_NONSTANDARD/index.html" \
    unittest2
  [[ "$status" -eq 1 ]]
  assert_not_found unittest2
}

@test "nonstandard: pip can install built packages" {
  pip install \
    --no-index \
    --find-links "https://s3-eu-west-1.amazonaws.com/$MKWHEELHOUSE_BUCKET_NONSTANDARD/index.html" \
    jinja2 pytsdb
}

@test "nonstandard: mkwheelhouse builds into prefix" {
  mkwheelhouse "$MKWHEELHOUSE_BUCKET_NONSTANDARD/deep/rooted/fear" zini
}

@test "nonstandard: pip can install built packages in prefix" {
  pip install \
    --no-index \
    --find-links "https://s3-eu-west-1.amazonaws.com/$MKWHEELHOUSE_BUCKET_NONSTANDARD/deep/rooted/fear/index.html" \
    zini
}

@test "nonstandard: pip can't install non-prefixed packages from prefix" {
  run pip install \
    --no-index \
    --find-links "https://s3-eu-west-1.amazonaws.com/$MKWHEELHOUSE_BUCKET_NONSTANDARD/deep/rooted/fear/index.html" \
    jinja2
  [[ "$status" -eq 1 ]]
  assert_not_found jinja2
}

@test "nonstandard: pip can't install packages from acl private" {
  run pip install \
    --no-index \
    --find-links "https://s3-eu-west-1.amazonaws.com/$MKWHEELHOUSE_BUCKET_NONSTANDARD-private/index.html" \
    jinja2
  [[ "$status" -eq 1 ]]
  assert_not_found jinja2
}

@test "nonstandard: install with acl public-read" {
  mkwheelhouse --acl public-read "$MKWHEELHOUSE_BUCKET_NONSTANDARD-private" jinja2
}

@test "nonstandard: pip can install packages from acl public-read" {
  pip install \
    --no-index \
    --find-links "https://s3-eu-west-1.amazonaws.com/$MKWHEELHOUSE_BUCKET_NONSTANDARD-private/index.html" \
    jinja2
}
