use leptos::*;
use reqwasm::http::Request;

#[component]
fn App() -> impl IntoView {
    let (api_status, set_api_status) = create_signal("Not Connected".to_string());

    let check_api = move |_| {
        spawn_local(async move {
            match Request::get("http://localhost:3000/health").send().await {
                Ok(resp) => {
                    if let Ok(text) = resp.text().await {
                        set_api_status.set(format!("Connected: {}", text));
                    }
                }
                Err(_) => {
                    set_api_status.set("Not Connected".to_string());
                }
            }
        });
    };

    view! {
        <div class="max-w-2xl mx-auto bg-white p-6 rounded-lg shadow-md">
            <h1 class="text-3xl font-bold text-blue-600 mb-4">"ZoomThai Procurement Intelligence"</h1>
            <p class="mb-4 text-gray-600">"เทสระบบ"</p>
            
            <button 
                on:click=check_api
                class="bg-blue-500 hover:bg-blue-600 text-white font-semibold py-2 px-4 rounded"
            >
                "ทดสอบเชื่อมต่อ API"
            </button>
            
            <div class="mt-6 p-4 bg-gray-50 border border-gray-200 rounded">
                <h2 class="text-sm font-semibold text-gray-500 mb-2">"สถานะ API:"</h2>
                <pre class="whitespace-pre-wrap text-sm">{api_status}</pre>
            </div>
        </div>
    }
}

fn main() {
    leptos::mount_to_body(App)
}