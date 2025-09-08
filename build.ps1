Param(
    [switch]$Clean,
    [switch]$View
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Ensure-ToolExists {
    param(
        [Parameter(Mandatory = $true)][string]$ToolName
    )
    $cmd = Get-Command $ToolName -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "No se encontró '$ToolName' en el PATH. Instala MiKTeX o TeX Live y asegúrate de que '$ToolName' esté disponible."
    }
    return $cmd.Source
}

function Remove-AuxFiles {
    $auxFiles = @(
        'main.log', 'main.aux', 'main.blg', 'main.out', 'main.bbl',
        'missfont.log', 'main.lof', 'main.lot', 'main.toc'
    )
    foreach ($f in $auxFiles) {
        Remove-Item -LiteralPath $f -ErrorAction SilentlyContinue
    }
}

function Run-XeLaTeX {
    Write-Host "Compilando con XeLaTeX..." -ForegroundColor Cyan
    & xelatex -interaction=nonstopmode -halt-on-error main.tex | Out-Host
    if ($LASTEXITCODE -ne 0) {
        throw "XeLaTeX falló. Revisa 'main.log' para detalles. Si 'main.pdf' está abierto en un visor (p. ej., Adobe), ciérralo e inténtalo de nuevo."
    }
}

function Run-BibTeXIfNeeded {
    if (Test-Path -LiteralPath 'main.aux') {
        $needsBib = Select-String -Path 'main.aux' -Pattern '\\citation|\\bibdata|\\bibstyle' -Quiet
        if ($needsBib) {
            Write-Host "Ejecutando BibTeX..." -ForegroundColor Cyan
            & bibtex main | Out-Host
            if ($LASTEXITCODE -ne 0) {
                throw "BibTeX falló. Revisa 'main.blg' para detalles."
            }
        }
        else {
            Write-Host "No se detectaron citas; se omite BibTeX." -ForegroundColor DarkYellow
        }
    }
}

try {
    if ($Clean) { Remove-AuxFiles }

    Ensure-ToolExists -ToolName 'xelatex' | Out-Null
    $bibtexPresent = $true
    try { Ensure-ToolExists -ToolName 'bibtex' | Out-Null } catch { $bibtexPresent = $false }
    if (-not $bibtexPresent) { Write-Host "Advertencia: 'bibtex' no está en PATH. Intentaré compilar sin bibliografía." -ForegroundColor DarkYellow }

    Run-XeLaTeX
    if ($bibtexPresent) { Run-BibTeXIfNeeded }
    Run-XeLaTeX
    Run-XeLaTeX

    if (Test-Path -LiteralPath 'main.pdf') {
        $pdfPath = Resolve-Path -LiteralPath 'main.pdf'
        Write-Host ("PDF generado: {0}" -f $pdfPath) -ForegroundColor Green
        if ($View) { Start-Process $pdfPath }
        exit 0
    }
    else {
        throw "La compilación terminó sin errores pero no se encontró 'main.pdf'. Revisa 'main.log'."
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}


