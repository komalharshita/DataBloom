# DataBloom — Copilot Instructions

## Product

DataBloom is an AI-powered data storytelling product.

Tagline:

"Turn raw data into a story people can understand."

Core experience:

Upload data → Analyze → Visualize → Explain → Discover insights.

The product should feel like a premium, approachable AI analytics product rather than a generic dashboard or developer tool.

---

## Current Task Priority

When working on frontend/UI tasks, prioritize:

1. UX clarity
2. Visual hierarchy
3. Premium visual design
4. Responsive behavior
5. Accessibility
6. Reusability
7. Performance

Do not change backend architecture unless explicitly requested.

Do not break existing API contracts.

Do not remove working functionality.

---

## Visual Identity

Use a visual language inspired by the provided Tellet reference:

- soft pastel pink backgrounds
- deep forest green primary color
- pink accent color
- warm white surfaces
- large rounded corners
- generous whitespace
- bold editorial typography
- subtle shadows
- restrained gradients
- premium SaaS aesthetic

Do not copy Tellet's branding, text, logo, content, or exact layouts.

Translate the visual language into DataBloom's own identity.

---

## Brand Personality

DataBloom should feel:

- intelligent
- approachable
- optimistic
- trustworthy
- modern
- human
- premium

Avoid:

- overly technical interfaces
- generic admin dashboards
- excessive neon/futuristic styling
- excessive animation
- clutter
- childish visual treatment

---

## UX Principle

The primary question the interface should answer is:

"What did DataBloom discover?"

The analysis/results screen is the most important product screen.

Prioritize insights and evidence over technical implementation details.

---

## Components

Prefer reusable components such as:

- Navbar
- Button
- UploadZone
- DatasetSummary
- MetricCard
- AnalysisProgress
- ChartCard
- InsightCard
- DataQualityCard
- RecommendationCard
- EmptyState
- ErrorState
- SectionHeader
- AnalysisTabs

Do not duplicate styles unnecessarily.

---

## Accessibility

Maintain:

- sufficient color contrast
- keyboard accessibility
- visible focus states
- semantic headings
- accessible labels
- meaningful chart titles
- information that is not communicated by color alone

---

## Engineering

Before modifying code:

1. Inspect the existing implementation.
2. Understand existing components and routes.
3. Reuse existing functionality.
4. Make the smallest appropriate change.
5. Run relevant tests/builds.
6. Check the actual rendered UI when possible.

Never claim that something works without testing it.

Do not add dependencies unless necessary.

Do not expose API keys or secrets.

Do not commit `.env` files.

---

## Deadline

DataBloom is a hackathon project with a very short deadline.

Prefer a reliable, polished implementation over ambitious architecture.

Do not introduce:

- authentication
- payments
- unnecessary databases
- microservices
- unnecessary agent frameworks
- unrelated features

unless explicitly requested.

---

## UI Rule

The application should look polished enough to be presented in a hackathon demo and captured in screenshots.

The final interface should feel intentional, cohesive, and production-quality.