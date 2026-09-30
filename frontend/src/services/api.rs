use gloo_net::http::Request;
use crate::models::procurement::ApiResponse;
use crate::environments::ENV; 

pub async fn fetch_items(id: &str) -> Result<ApiResponse, String> {
    let encoded_id = urlencoding::encode(id);
    let url = format!("{}/announcements/{}/items", ENV.api_base_url, encoded_id);
    
    let response = Request::get(&url)
        .send()
        .await
        .map_err(|e| e.to_string())?;
        
    let data = response
        .json::<ApiResponse>()
        .await
        .map_err(|e| e.to_string())?;
        
    Ok(data)
}