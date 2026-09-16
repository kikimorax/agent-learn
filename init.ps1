# 该脚本用于初始化环境，包括安装uv, 并使用uv安装python
# uv: https://docs.astral.sh/uv/

if ($env:AGENT_LEARN_BYPASS_RELAUNCHED -ne '1') {
	$env:AGENT_LEARN_BYPASS_RELAUNCHED = '1'
	& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $PSCommandPath @args
	exit $LASTEXITCODE
}

# 安装uv
Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression

# uv python install --default --preview-features python-install-default --force