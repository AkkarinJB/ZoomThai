use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Default)]
pub struct Announcement {
    pub id: String,
    pub agency: String,
    pub title: String,
    pub method: Option<String>,
    #[serde(rename = "fiscalYear")]
    pub fiscal_year: Option<i32>,
    #[serde(rename = "budgetAmount")]
    pub budget_amount: Option<String>,
    #[serde(rename = "submissionDeadline")]
    pub submission_deadline: Option<String>,
    #[serde(rename = "torPdfPath")]
    pub tor_pdf_path: Option<String>,
}

#[derive(Serialize, Clone, Debug, Default)]
pub struct SearchFilters {
    #[serde(skip_serializing_if = "Vec::is_empty")]
    pub agency: Vec<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub budget_min: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub budget_max: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub method: Option<String>,
}

#[derive(Serialize, Clone, Debug)]
pub struct SearchRequest {
    pub query: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub filters: Option<SearchFilters>,
    pub limit: i32,
    pub offset: i32,
}

#[derive(Serialize, Deserialize, Clone, Debug, Default)]
pub struct SearchResponse {
    pub total: i32,
    pub query_time_ms: f64,
    pub items: Vec<Announcement>,
}

#[derive(Serialize, Clone, Debug)]
pub struct AskRequest {
    pub question: String,
    pub top_k: i32,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq, Default)]
pub struct Citation {
    pub announcement_id: String,
    pub text_snippet: String,
    pub page_number: i32,
}

#[derive(Deserialize, Clone, Debug, Default)]
pub struct AskResponse {
    pub answer: Option<String>,
    pub citations: Option<Vec<Citation>>,
    pub confidence: Option<f64>,
    pub reasoning: Option<String>,
    pub unable_reason: Option<String>,
}
