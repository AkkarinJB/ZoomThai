use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct ProcurementItem {
    pub id: i32,
    #[serde(rename = "announcementId")]
    pub announcement_id: String,
    #[serde(rename = "lineNo")]
    pub line_no: Option<i32>,
    #[serde(rename = "itemCode")]
    pub item_code: Option<String>,
    pub description: Option<String>,
    pub quantity: Option<String>,
    pub unit: Option<String>,
    #[serde(rename = "unitPriceEstimate")]
    pub unit_price_estimate: Option<String>,
    #[serde(rename = "totalPriceEstimate")]
    pub total_price_estimate: Option<String>,
}

#[derive(Serialize, Deserialize, Clone, Debug, PartialEq)]
pub struct ApiResponse {
    pub announcement_id: String,
    pub total_items: usize,
    pub items: Vec<ProcurementItem>,
}