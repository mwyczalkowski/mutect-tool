class: Workflow
cwlVersion: v1.0
id: mutectworkflow
label: MutectWorkflow
$namespaces:
  sbg: 'https://www.sevenbridges.com/'
inputs:
  - id: tumor
    type: File
    'sbg:x': -366.39886474609375
    'sbg:y': -190
  - id: reference
    type: File
    'sbg:x': -398.39886474609375
    'sbg:y': -71
  - id: normal
    type: File
    'sbg:x': -327.39886474609375
    'sbg:y': 61
outputs:
  - id: mutations
    outputSource:
      - mutect/mutations
    type: File
    'sbg:x': 78.60113525390625
    'sbg:y': -189
steps:
  - id: mutect
    in:
      - id: normal
        source: normal
      - id: reference
        source: reference
      - id: tumor
        source: tumor
    out:
      - id: call_stats
      - id: coverage
      - id: mutations
    run: ./mutect.cwl
    label: MuTect
    'sbg:x': -142.3984375
    'sbg:y': -73
requirements: []
