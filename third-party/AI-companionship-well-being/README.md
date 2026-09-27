# Interaction with AI Companions and Psychological Well-being

This repository provides the de-identified quantitative data and statistical analysis code needed to reproduce the main findings of the study "Interaction with AI Companions and Psychological Well-being", together with the browser extension used to collect chat-history donations from Character.AI users.

## Data availability

The de-identified quantitative data are available in this repository (`data.csv`). Raw chat history data are not publicly available: they contain potentially sensitive personal information and were collected under consent agreements that do not permit data sharing, and even after de-identification the conversational nature of the data poses a substantial risk of participant re-identification. To support interpretation and verification of the qualitative findings while preserving participant privacy, de-identified and processed materials, including all prompts, the topic-modeling evaluation procedure, and example outputs from topic modeling on chatbot-user conversations, self-disclosure, and self-reported positive/negative influences, are provided in the Supplementary Information of the paper.

## Repository structure

```text
.
├── data.csv
├── AI_companionship_analysis_r_code.Rmd
└── data_donation_extension/
```

### `data.csv`

De-identified participant-level dataset used for the primary analyses reported in the paper. All personally identifiable information has been removed or anonymized. Variables correspond to the survey measures and derived indices described in the Methods section and Supplementary Information of the manuscript, including:

- Subjective well-being (six items from the Comprehensive Inventory of Thriving).
- Chatbot interaction intensity (seven-item composite adapted from the Facebook Intensity Scale).
- Self-disclosure to chatbots (subscale adapted from the Message Orientation in ComputerMediated Communicatio instrument).
- Offline social network size (adapted from the Lubben Social Network Scale).
- Companionship usage indicators derived from the forced-choice survey item and from LLM-based classification of free-text relationship descriptions.
- Demographic and control variables (gender, romantic relationship status, tenure of Character.AI use, age).

### `AI_companionship_analysis_r_code.Rmd`

R Markdown file containing the analysis code used in the study. All statistical analyses were conducted in R version 4.5.0. The script reproduces the multivariate regression analyses reported in the paper and the Heckman selection models used to address potential bias in the chat-history donation subsample. All hypothesis tests are two-tailed; normality of residuals and homoscedasticity are checked prior to linear regression.

### `data_donation_extension/`

Source code for the custom Google Chrome extension developed for this study. The extension allowed participants to export their Character.AI conversation logs in JSON format, review them, and optionally redact sensitive content prior to submission. All processing occurred locally on the participant's device, and no raw chat data were transmitted to external servers or APIs.

## Citation

Please cite our paper if you use this code or part of it in your work:

```bibtex
@article{zhang2026interaction,
  title={Interaction with AI companions and psychological well-being},
  author={Zhang, Yutong and Zhao, Dora and Hancock, Jeffrey T. and Kraut, Robert and Yang, Diyi},
  journal={Nature Human Behaviour},
  year={2026},
  doi={10.1038/s41562-026-02516-2},
  url={https://doi.org/10.1038/s41562-026-02516-2}
}
```
