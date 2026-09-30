use gloo_net::http::Request;
use crate::models::procurement::ApiResponse;
use crate::models::search::{AskRequest, AskResponse, SearchRequest, SearchResponse};
use crate::environments::ENV;

pub async fn fetch_items(id: &str) -> Result<ApiResponse, String> {
    let encoded_id = urlencoding::encode(id);
    let url = format!("{}/announcements/{}/items", ENV.api_base_url, encoded_id);
    Request::get(&url)
        .send()
        .await
        .map_err(|e| e.to_string())?
        .json::<ApiResponse>()
        .await
        .map_err(|e| e.to_string())
}

pub async fn search_announcements(req: SearchRequest) -> Result<SearchResponse, String> {
    let url = format!("{}/search", ENV.api_base_url);
    Request::post(&url)
        .json(&req)
        .map_err(|e| e.to_string())?
        .send()
        .await
        .map_err(|e| e.to_string())?
        .json::<SearchResponse>()
        .await
        .map_err(|e| e.to_string())
}

pub async fn ask_question(req: AskRequest) -> Result<AskResponse, String> {
    let url = format!("{}/ask", ENV.api_base_url);
    Request::post(&url)
        .json(&req)
        .map_err(|e| e.to_string())?
        .send()
        .await
        .map_err(|e| e.to_string())?
        .json::<AskResponse>()
        .await
        .map_err(|e| e.to_string())
}