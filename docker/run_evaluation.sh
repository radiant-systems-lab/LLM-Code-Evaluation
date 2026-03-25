#!/bin/bash
# =============================================================================
# Transitive Dependency Evaluation Script
# Runs each project in a fresh Docker container with zero cached dependencies.
# Output: CSV with agent, project, language, claimed_count, transitive_count
# =============================================================================

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GENERATED="$REPO_ROOT/generated_code"
RESULTS_DIR="$REPO_ROOT/docker/results"
mkdir -p "$RESULTS_DIR"

# Build images (or use prebuilt)
echo "Building Docker images..."
docker build -t eval-python -f "$REPO_ROOT/docker/Dockerfile.python" "$REPO_ROOT/docker"
docker build -t eval-javascript -f "$REPO_ROOT/docker/Dockerfile.javascript" "$REPO_ROOT/docker"
docker build -t eval-java -f "$REPO_ROOT/docker/Dockerfile.java" "$REPO_ROOT/docker"

# =============================================================================
# PYTHON EVALUATION
# =============================================================================
PYRESULTS="$RESULTS_DIR/python_transitive.csv"
echo "agent,project,language,claimed_count,transitive_count" > "$PYRESULTS"

echo ""
echo "=== Evaluating Python projects ==="
for agent in claude codex gemini; do
    for proj_dir in "$GENERATED/$agent/python"/p_*; do
        proj=$(basename "$proj_dir")
        reqfile=$(find "$proj_dir" -maxdepth 1 -name '*requirements*.txt' | head -1)
        [ -z "$reqfile" ] && continue

        # Skip stdlib-only projects
        if head -1 "$reqfile" | grep -qiE '^(none|$|\(none|\(empty)'; then
            echo "  Py ${agent}/${proj} (stdlib)... 0"
            echo "${agent},${proj},python,0,0" >> "$PYRESULTS"
            continue
        fi

        claimed=$(grep -cE '^[a-zA-Z]' "$reqfile" 2>/dev/null || echo "0")
        echo -n "  Py ${agent}/${proj} (claimed=${claimed})... "

        result=$(docker run --rm \
            -v "$reqfile:/work/requirements.txt:ro" \
            eval-python sh -c '
                pip install -r /work/requirements.txt --quiet --no-warn-script-location 2>/dev/null
                rc=$?
                if [ $rc -ne 0 ]; then
                    sed "s/[>=<]=.*//g; s/\[.*\]//g" /work/requirements.txt > /tmp/relaxed.txt
                    pip install -r /tmp/relaxed.txt --quiet --no-warn-script-location 2>/dev/null
                fi
                pip list --format=freeze 2>/dev/null | grep -v "^pip=\|^setuptools=\|^wheel=" | wc -l
            ' 2>/dev/null | tail -1)

        [ -z "$result" ] && result="ERROR"
        echo "transitive=${result}"
        echo "${agent},${proj},python,${claimed},${result}" >> "$PYRESULTS"
    done
done

# =============================================================================
# JAVASCRIPT EVALUATION
# =============================================================================
JSRESULTS="$RESULTS_DIR/javascript_transitive.csv"
echo "agent,project,language,claimed_count,transitive_count" > "$JSRESULTS"

echo ""
echo "=== Evaluating JavaScript projects ==="
for agent in claude codex gemini; do
    for proj_dir in "$GENERATED/$agent/javascript"/p_*; do
        proj=$(basename "$proj_dir")
        [ ! -f "$proj_dir/package.json" ] && continue

        claimed=$(python3 -c "
import json
d=json.load(open('$proj_dir/package.json'))
print(len(d.get('dependencies',{})))
" 2>/dev/null || echo "0")

        echo -n "  JS ${agent}/${proj} (claimed=${claimed})... "

        result=$(docker run --rm \
            -v "$proj_dir/package.json:/work/package.json:ro" \
            eval-javascript sh -c '
                cd /work
                npm install --ignore-scripts --no-audit --no-fund >/dev/null 2>&1
                npm list --all --parseable 2>/dev/null | tail -n +2 | wc -l
            ' 2>/dev/null | tail -1)

        [ -z "$result" ] && result="ERROR"
        echo "transitive=${result}"
        echo "${agent},${proj},javascript,${claimed},${result}" >> "$JSRESULTS"
    done
done

# =============================================================================
# JAVA EVALUATION
# =============================================================================
JAVARESULTS="$RESULTS_DIR/java_transitive.csv"
echo "agent,project,language,claimed_count,transitive_count" > "$JAVARESULTS"

echo ""
echo "=== Evaluating Java projects ==="
for agent in claude codex gemini; do
    for proj_dir in "$GENERATED/$agent/java"/p_*; do
        proj=$(basename "$proj_dir")
        [ ! -f "$proj_dir/pom.xml" ] && continue

        claimed=$(grep -c '<dependency>' "$proj_dir/pom.xml" 2>/dev/null || echo "0")
        echo -n "  Java ${agent}/${proj} (claimed=${claimed})... "

        result=$(docker run --rm \
            -v "$proj_dir/pom.xml:/work/pom.xml:ro" \
            eval-java sh -c '
                mkdir -p /build/src/main/java && cd /build
                cp /work/pom.xml .
                output=$(mvn dependency:tree 2>/dev/null)
                count=$(echo "$output" | grep -E "^\[INFO\] [|+\\\\]" | wc -l)
                if [ "$count" = "0" ]; then
                    count=$(echo "$output" | grep -E "^\[INFO\].*:.*:.*:.*:.*" | grep -v "BUILD\|maven-\|Scanning\|---\|Downloading\|Downloaded\|Progress" | wc -l)
                    count=$((count > 0 ? count - 1 : 0))
                fi
                echo "$count"
            ' 2>/dev/null | tail -1)

        [ -z "$result" ] && result="ERROR"
        echo "transitive=${result}"
        echo "${agent},${proj},java,${claimed},${result}" >> "$JAVARESULTS"
    done
done

echo ""
echo "=== EVALUATION COMPLETE ==="
echo "Results saved to:"
echo "  $PYRESULTS"
echo "  $JSRESULTS"
echo "  $JAVARESULTS"
