use leptos::*;
use leptos_router::*;

#[component]
pub fn Home() -> impl IntoView {
    let (search_query, set_search_query) = create_signal(String::new());
    let navigate = use_navigate();

    let on_search = move |ev: leptos::ev::SubmitEvent| {
        ev.prevent_default();
        let query = search_query.get();
        if !query.is_empty() {
            let encoded_query = urlencoding::encode(&query);
            navigate(&format!("/announcements/{}", encoded_query), Default::default());
        }
    };

    view! {
        <div class="flex items-center justify-center min-h-[80vh]">
            <div class="bg-white p-10 rounded-2xl shadow-xl border border-gray-200 max-w-lg w-full text-center">
                <h1 class="text-4xl font-extrabold text-blue-900 mb-4">"ZoomThai"</h1>
                <p class="text-gray-500 mb-8">"ระบบสืบค้นข้อมูลจัดซื้อจัดจ้าง"</p>
                
                <form on:submit=on_search class="flex flex-col gap-4">
                    <input 
                        type="text" 
                        placeholder="กรอกรหัสประกาศ (เช่น PEA-TDDP.2(A)-082/2564)" 
                        class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                        on:input=move |ev| set_search_query.set(event_target_value(&ev))
                        prop:value=search_query
                    />
                    <button 
                        type="submit" 
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg transition-colors shadow-md">
                        "ค้นหารายการ"
                    </button>
                </form>
            </div>
        </div>
    }
}