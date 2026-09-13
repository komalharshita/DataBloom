export type Visualization = {
  title: string;
  type: string;
  x: string;
  y?: string;
  x_data?: unknown[];
  y_data?: unknown[];
  insight?: string;
  rationale?: string;
};

export type Result = {
  summary?: string;
  executive_summary?: string;
  key_metrics?: { name: string; value: string }[];
  visualizations?: Visualization[];
  insights?: string[];
  recommendations?: string[];
  data_quality?: { issue: string; severity: string }[];
  overview?: { rows?: number };
};

const cleanDataQuality = [{
  issue: "No missing values or duplicate rows were detected across the 24 records.",
  severity: "low",
}];

export const PRECOMPUTED_SAMPLE_STORIES: Record<string, Result> = {
  sales: {
    summary: "Revenue reached $392,800 across 24 weekly records, with May as the strongest month and East as the leading region. Cloud Desk sold the most units, while Analytics Suite generated the most revenue.",
    executive_summary: "Revenue reached $392,800 across 24 weekly records, with May as the strongest month and East as the leading region. Cloud Desk sold the most units, while Analytics Suite generated the most revenue.",
    key_metrics: [
      { name: "Total revenue", value: "$392,800" },
      { name: "Units sold", value: "1,201" },
      { name: "Top region", value: "East ($102,900)" },
      { name: "Top product revenue", value: "Analytics Suite ($160,900)" },
    ],
    visualizations: [
      {
        title: "Revenue by month",
        type: "bar",
        x: "Month",
        y: "Revenue",
        x_data: ["2024-01", "2024-02", "2024-03", "2024-04", "2024-05", "2024-06"],
        y_data: [57200, 60800, 58600, 65300, 80400, 70500],
        rationale: "A monthly bar chart makes the changing revenue level easy to compare across the six-month period.",
        insight: "May is the peak month at $80,400, 40.6% above January's $57,200.",
      },
      {
        title: "Revenue by region",
        type: "bar",
        x: "Region",
        y: "Revenue",
        x_data: ["East", "North", "South", "West"],
        y_data: [102900, 97700, 97200, 95000],
        rationale: "A category comparison shows where revenue is concentrated without implying that region alone caused the difference.",
        insight: "East leads West by $7,900, while the four regions remain relatively close in total revenue.",
      },
      {
        title: "Revenue by product",
        type: "pie",
        x: "Product",
        y: "Revenue",
        x_data: ["Analytics Suite", "Cloud Desk", "Security Hub"],
        y_data: [160900, 142000, 89900],
        rationale: "A part-to-whole view shows each product's share of the $392,800 revenue total.",
        insight: "Analytics Suite contributes 41.0% of revenue, ahead of Cloud Desk at 36.1%.",
      },
    ],
    insights: [
      "Revenue rose from $57,200 in January to $70,500 in June, with a May peak of $80,400.",
      "East is the highest-revenue region at $102,900, and West is the lowest at $95,000.",
      "Cloud Desk accounts for 565 of 1,201 units sold, while Analytics Suite leads revenue at $160,900.",
    ],
    recommendations: [
      "Investigate what changed in May before planning the next sales push, since it is the strongest month in the period.",
      "Use Cloud Desk's unit volume and Analytics Suite's revenue contribution to compare volume-led and value-led growth opportunities.",
    ],
    data_quality: cleanDataQuality,
    overview: { rows: 24 },
  },
  logistics: {
    summary: "The operation delivered 14 of 24 shipments on time and handled 2,086 packages. SwiftShip was on time for all nine of its shipments, while RapidRoute had the highest average delay at 23.67 hours.",
    executive_summary: "The operation delivered 14 of 24 shipments on time and handled 2,086 packages. SwiftShip was on time for all nine of its shipments, while RapidRoute had the highest average delay at 23.67 hours.",
    key_metrics: [
      { name: "Packages handled", value: "2,086" },
      { name: "On-time shipments", value: "14 of 24 (58.3%)" },
      { name: "Average delay", value: "9.33 hours" },
      { name: "Average delivery", value: "3.56 days" },
    ],
    visualizations: [
      {
        title: "Average delay by carrier",
        type: "bar",
        x: "Carrier",
        y: "Average delay (hours)",
        x_data: ["SwiftShip", "ParcelPro", "RapidRoute"],
        y_data: [0, 9.11, 23.67],
        rationale: "Comparing average delay by carrier isolates the clearest operational difference in the shipment records.",
        insight: "RapidRoute averages 23.67 hours of delay, compared with 0 for SwiftShip.",
      },
      {
        title: "Packages by carrier",
        type: "bar",
        x: "Carrier",
        y: "Packages",
        x_data: ["SwiftShip", "ParcelPro", "RapidRoute"],
        y_data: [877, 753, 456],
        rationale: "A volume comparison adds scale to the carrier reliability picture and avoids judging delay without workload context.",
        insight: "SwiftShip handled the most packages at 877 while maintaining all 9 shipments on time.",
      },
      {
        title: "Average delay by region",
        type: "bar",
        x: "Region",
        y: "Average delay (hours)",
        x_data: ["North", "South", "East", "West"],
        y_data: [8, 19.17, 2, 8.17],
        rationale: "Regional comparison highlights where delivery delays are concentrated across the network.",
        insight: "South has the highest average delay at 19.17 hours, while East averages 2 hours.",
      },
    ],
    insights: [
      "Only 58.3% of shipments were on time, so 10 of 24 shipments arrived late.",
      "RapidRoute had six shipments and no on-time deliveries; its average delay was 23.67 hours.",
      "South is the slowest region at 19.17 average delay hours, while East handled 649 packages with a 2-hour average delay.",
    ],
    recommendations: [
      "Review RapidRoute's South and North Hub - Rural shipments first, because the carrier has the highest delay average and no on-time records.",
      "Compare the operating conditions behind SwiftShip's 9-for-9 on-time record before changing carrier allocation.",
    ],
    data_quality: cleanDataQuality,
    overview: { rows: 24 },
  },
  people: {
    summary: "The 24-person snapshot averages 4.09 for performance and 3.96 for satisfaction. Support is the clear risk concentration: all four high-risk employees are in Support, where average satisfaction is 3.12 and monthly absences average 4.2.",
    executive_summary: "The 24-person snapshot averages 4.09 for performance and 3.96 for satisfaction. Support is the clear risk concentration: all four high-risk employees are in Support, where average satisfaction is 3.12 and monthly absences average 4.2.",
    key_metrics: [
      { name: "Employees", value: "24" },
      { name: "Average performance", value: "4.09 / 5" },
      { name: "Average satisfaction", value: "3.96 / 5" },
      { name: "High attrition risk", value: "4 employees" },
    ],
    visualizations: [
      {
        title: "Performance by department",
        type: "bar",
        x: "Department",
        y: "Average performance score",
        x_data: ["Engineering", "Sales", "Finance", "Marketing", "People", "Support"],
        y_data: [4.48, 4.4, 4.33, 4.13, 3.93, 3.3],
        rationale: "Department averages make differences in performance visible while preserving the 1-to-5 score scale.",
        insight: "Engineering has the highest average performance at 4.48; Support is lowest at 3.30.",
      },
      {
        title: "Satisfaction by department",
        type: "bar",
        x: "Department",
        y: "Average satisfaction score",
        x_data: ["People", "Engineering", "Finance", "Sales", "Marketing", "Support"],
        y_data: [4.33, 4.38, 4.23, 4.08, 3.83, 3.12],
        rationale: "A department comparison shows where employee sentiment differs most across the organization.",
        insight: "Support's 3.12 average satisfaction is 1.26 points below Engineering's 4.38.",
      },
      {
        title: "Attrition risk mix",
        type: "pie",
        x: "Attrition risk",
        y: "Employees",
        x_data: ["Low", "Medium", "High"],
        y_data: [14, 6, 4],
        rationale: "A part-to-whole view shows the distribution of the three recorded attrition-risk levels.",
        insight: "Four of 24 employees are high risk and six are medium risk, so 10 employees are not low risk.",
      },
    ],
    insights: [
      "Support contains all four high-risk employees and has the lowest department averages for performance (3.30) and satisfaction (3.12).",
      "Support also averages 4.2 monthly absences, compared with 0.67 in Finance and People.",
      "Engineering leads performance at 4.48 and satisfaction at 4.38 among the larger departments in this snapshot.",
    ],
    recommendations: [
      "Prioritize a Support-focused review of workload, satisfaction, and absence patterns because the high-risk records are concentrated there.",
      "Compare the practices behind Engineering's stronger scores with Support's conditions before choosing an intervention.",
    ],
    data_quality: cleanDataQuality,
    overview: { rows: 24 },
  },
};
