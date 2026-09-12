# DataBloom Engineering Constitution

## Product

DataBloom is an AI-powered data storytelling application.

Tagline:

"Turn raw data into a story people can understand."

The product transforms uploaded structured datasets into:

1. Dataset understanding
2. Key metrics
3. Meaningful visualizations
4. Plain-English insights
5. Executive-level recommendations

---

## Core principle

DataBloom is NOT a generic chatbot.

AI must be used for meaningful data analysis, visualization selection, and storytelling.

---

## Architecture principle

Prefer:

Deterministic code for:

* file parsing
* schema detection
* statistics
* calculations
* validation
* chart rendering

Use AI for:

* analytical interpretation
* visualization selection
* natural-language reasoning
* insight generation
* storytelling

Never ask an LLM to perform deterministic work unnecessarily.

---

## Grounding rule

Every factual claim must be supported by the uploaded dataset or an explicitly calculated statistic.

The system must never:

* invent values
* invent columns
* invent trends
* invent relationships
* invent causal explanations
* fabricate recommendations
* fabricate evaluation metrics

If the data only supports association, use associative language.

---

## Visualization rule

Choose visualizations based on analytical intent.

Examples:

Time series → line chart

Category comparison → bar chart

Distribution → histogram/box plot

Relationship → scatter plot

Correlation → heatmap

Geographical comparison → map when appropriate

Do not choose charts purely for aesthetics.

---

## Agent architecture

DataBloom should use five logical components:

1. Data Profiler
2. Data Analyst
3. Visualization Agent
4. Storyteller
5. Validator

Not every component needs to be an autonomous LLM agent.

Prefer deterministic Python pipelines wherever possible.

---

## Structured output

All AI outputs must conform to Pydantic schemas.

Do not allow arbitrary unvalidated model output to directly control the frontend.

---

## Visualization safety

The model must reference only columns that actually exist.

The application must validate visualization specifications before rendering.

---

## Validation

The Validator should be able to reject AI output when:

* a column does not exist
* a value is unsupported
* the chart type is incompatible
* JSON is malformed
* insight contradicts calculated data
* required fields are missing

When possible, automatically regenerate the invalid component.

---

## Product priorities

Priority order:

1. Working application
2. Reliable AI analysis
3. Data grounding
4. Useful visualizations
5. Excellent UX
6. Evaluation
7. Deployment
8. Documentation
9. Optional features

Do not sacrifice reliability for architectural complexity.

---

## Engineering rules

* TypeScript on frontend.
* Python on backend.
* FastAPI for APIs.
* Pandas for data processing.
* Plotly for visualization.
* Pydantic for structured validation.
* Environment variables for secrets.
* Never commit API keys.
* Keep modules small and testable.
* Avoid unnecessary dependencies.
* Test after major changes.
* Never claim a feature works without testing it.

---

## AI model strategy

The first working version may use a strong API model.

Do not block the application on fine-tuning.

A specialized open model such as Qwen3-8B may be evaluated later using the project dataset.

Compare the specialized model against the baseline rather than assuming fine-tuning improves performance.

---

## Human-in-the-loop

The human engineer is responsible for:

* API credentials
* external authentication
* dataset provision
* deployment credentials
* manual acceptance testing
* final product decisions

When a human-only action is required, stop and clearly state:

HUMAN ACTION REQUIRED

Never fabricate credentials or external-service results.

---

## Development process

Work in three phases:

Phase 1:
Build working MVP.

Phase 2:
Integrate and evaluate the dataset/model.

Phase 3:
Polish, test and deploy.

Do not move to the next phase without completing the current phase.

---

## Hackathon principle

Build a reliable, demonstrable product rather than an unnecessarily complex research system.

The application must be understandable within a 60–90 second live demo.
