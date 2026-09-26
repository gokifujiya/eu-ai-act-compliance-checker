# ============================================================
# add_explanations.ps1
# PDF-faithful guidance for the EU AI Act Compliance Checker
# ============================================================

$path = "data\processed\compliance_rules.json"

$r = Get-Content $path -Raw | ConvertFrom-Json


# ============================================================
# First remove ALL previously added guidance.
# This prevents old/non-PDF explanations from surviving.
# ============================================================

"E1","E2","E3","HR1","HR2","HR3","HR4","HR5","HR6","S1","R1","R2","R3","R4","R5" |
ForEach-Object {
    $q = $r.$_

    if ($null -ne $q -and $q.PSObject.Properties.Name -contains "guidance") {
        $q.PSObject.Properties.Remove("guidance")
    }
}


# ============================================================
# E1
#
# The first item is the PDF's introductory AI-system
# definition immediately preceding E1.
#
# The remaining items are E1's actual Hint.
# ============================================================

$r.E1 | Add-Member -NotePropertyName guidance -NotePropertyValue @(
    "AI system: A machine-based system designed to operate with varying levels of autonomy and that may exhibit adaptiveness after deployment and that, for explicit or implicit objectives, infers, from the input it receives, how to generate outputs such as predictions, content, recommendations, or decisions that can influence physical or virtual environments.",

    "Note: It is possible to be multiple types of entity at once, according to Recital 83. If you match the definition of multiple types, you must complete the questionnaire once for each type.",

    "Provider: a natural or legal person, public authority, agency or other body that develops an AI system or a general purpose AI model (or that has an AI system or a general purpose AI model developed) and places them on the market or puts the system into service under its own name or trademark, whether for payment or free of charge;",

    "Deployer: any natural or legal person, public authority, agency or other body using an AI system under its authority except where the AI system is used in the course of a personal non professional activity;",

    "Distributor: any natural or legal person in the supply chain, other than the provider or the importer, that makes an AI system available on the Union market;",

    "Importer: any natural or legal person located or established in the Union that places on the market an AI system that bears the name or trademark of a natural or legal person established outside the Union;",

    "Product manufacturer: places on the market or puts into service an AI system together with their product and under their own name or trademark;",

    "Authorised representative: any natural or legal person located or established in the Union who has received and accepted a written mandate from a provider of an AI system or a general purpose AI model to, respectively, perform and carry out on its behalf the obligations and procedures established by this Regulation."
)


# ============================================================
# E2
#
# NO Hint in PDF.
#
# Correct the option itself to include the Article 3 point 23
# reference exactly where the PDF puts it.
# ============================================================

if ($null -ne $r.E2.options.substantial_modification) {
    $r.E2.options.substantial_modification.label =
        "Performing a substantial modification (see Article 3 point 23) to the system"
}


# ============================================================
# E3 — actual PDF Hint
# ============================================================

$r.E3 | Add-Member -NotePropertyName guidance -NotePropertyValue @(
    "Note: This applies ONLY if your product is placed on the market / put into service within the EU, regardless of whether or not you are established within the EU."
)


# ============================================================
# HR1
#
# NO Hint in PDF.
# ============================================================


# ============================================================
# HR2
#
# NO Hint in PDF.
# ============================================================


# ============================================================
# HR3 — actual PDF Hint
# ============================================================

$r.HR3 | Add-Member -NotePropertyName guidance -NotePropertyValue @(
    "How to answer this question: Each of the high risk categories in question #HR3 are associated with an existing EU law; see Annex I, Section A for a full list.",

    "These laws require some products to undergo third party conformity assessments. Please check the laws relevant to your product category(s) to see whether your product is required to undergo a third party conformity assessment under those laws.",

    "If your product is required to undergo a third party conformity assessment under any of these laws, please select Yes above. Otherwise, select No above.",

    "Some of these laws allow you to opt out of a third party conformity assessment. If you are given this option, you are able to do so if you meet the conditions outlined in Article 43(3). In this case you can select No above.",

    "If you're unsure, you may wish to consult a lawyer on this topic."
)


# ============================================================
# HR4 — actual PDF Hint
# ============================================================

$r.HR4 | Add-Member -NotePropertyName guidance -NotePropertyValue @(
    "Unsure? See definitions for each of these options in Annex III."
)


# ============================================================
# HR5 — actual PDF Hint
# ============================================================

$r.HR5 | Add-Member -NotePropertyName guidance -NotePropertyValue @(
    "The system does NOT pose a significant risk if one or more of the following conditions are met:",

    "The AI system is intended to perform a narrow procedural task.",

    "The AI system is intended to improve the result of a previously completed human activity.",

    "The AI system is intended to detect decision making patterns or deviations from prior decision making patterns and is not meant to replace or influence the previously completed human assessment, without proper human review.",

    "The AI system is intended to perform a preparatory task to an assessment relevant for the purpose of the use cases listed in Annex III.",

    "If your system meets any of these conditions, please select No above. If it meets none of these conditions, please select Yes above.",

    "Note: Your system is always considered to be high risk if it performs profiling of natural persons. If this applies to your system, please select Yes."
)


# ============================================================
# HR6 — actual PDF Hint
# ============================================================

$r.HR6 | Add-Member -NotePropertyName guidance -NotePropertyValue @(
    "Safety component: A component of a product or of a system which fulfils a safety function for that product or system, or the failure or malfunctioning of which endangers the health and safety of persons or property (Source: Article 3 point 14)."
)


# ============================================================
# S1 — actual PDF Hint
# ============================================================

$r.S1 | Add-Member -NotePropertyName guidance -NotePropertyValue @(
    "See here for a current list of EU Member States."
)


# ============================================================
# R1 — actual PDF Hint
# ============================================================

$r.R1 | Add-Member -NotePropertyName guidance -NotePropertyValue @(
    "High impact capabilities: an AI model is determined to have high impact capabilities if the cumulative amount of computation used for its training measured in floating point operations is greater than 10^25 (Source: Article 51 point 2)."
)


# ============================================================
# R2
#
# NO Hint in PDF.
# ============================================================


# ============================================================
# R3 — actual PDF Hint
# ============================================================

$r.R3 | Add-Member -NotePropertyName guidance -NotePropertyValue @(
    "Unsure? See definitions for each of these options in Article 5."
)


# ============================================================
# R4
#
# NO Hint in PDF.
# ============================================================


# ============================================================
# R5
#
# NO Hint in PDF.
# ============================================================


# ============================================================
# Write UTF-8 WITHOUT BOM
#
# PowerShell's Set-Content -Encoding utf8 may produce a BOM
# depending on PowerShell version, so use .NET explicitly.
# ============================================================

$json = $r | ConvertTo-Json -Depth 30

[System.IO.File]::WriteAllText(
    (Join-Path (Get-Location) $path),
    $json,
    [System.Text.UTF8Encoding]::new($false)
)

