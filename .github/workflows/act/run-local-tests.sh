#!/bin/bash

# スクリプトの絶対パスを取得
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# プロジェクトのルートディレクトリを取得
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"

# テスト結果を保存するディレクトリ
LOG_DIR="${PROJECT_ROOT}/.github/workflows/act/act_logs"
mkdir -p "${LOG_DIR}"

# テストを実行する関数
run_test() {
    local python_version="$1"
    local docker_image="python:${python_version}-slim"
    local log_file="${LOG_DIR}/act-wf-${python_version}.log"
    local workflow_file="${SCRIPT_DIR}/local-test.yml"

    echo "Running tests for Python ${python_version}"
    echo "Using Docker image: ${docker_image}"
    echo "Logging to: ${log_file}"
    echo "Workflow file: ${workflow_file}"

    # ワークフローファイルの存在を確認
    if [ ! -f "${workflow_file}" ]; then
        echo "❌ ワークフローファイルが見つかりません: ${workflow_file}"
        return 1
    fi

    # actコマンドの実行
    act pull_request \
        -W "${workflow_file}" \
        -P ubuntu-latest="${docker_image}" \
        --verbose 2>&1 | tee "${log_file}"

    local exit_code="${PIPESTATUS[0]}"
    if [ "$exit_code" -eq 0 ]; then
        echo "✅ テストに成功しました: Python ${python_version}"
    else
        echo "❌ テストに失敗しました: Python ${python_version}"
    fi
    echo "----------------------------------------"
    return "$exit_code"
}

# 結果を保存する配列
declare -A results

# 各バージョンでテストを実行
python_versions=("3.10" "3.11" "3.12" "3.13-rc")
failed_versions=()

for version in "${python_versions[@]}"; do
    if run_test "$version"; then
        results["$version"]="✅ 成功"
    else
        results["$version"]="❌ 失敗"
        failed_versions+=("$version")
    fi
done

# 結果のサマリーを表示
echo "テスト結果サマリー:"
echo "===================="
for version in "${python_versions[@]}"; do
    echo "Python ${version}: ${results["$version"]}"
done

# 失敗したテストがあれば報告
if [ "${#failed_versions[@]}" -ne 0 ]; then
    echo -e "\n失敗したテストのバージョン:"
    for version in "${failed_versions[@]}"; do
        echo "- Python ${version}"
    done
    exit 1
fi
