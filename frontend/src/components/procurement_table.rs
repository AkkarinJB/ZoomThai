use leptos::*;
use leptos_router::*;
use crate::services::api::fetch_items;

#[component]
pub fn ProcurementTable() -> impl IntoView {

    let params = use_params_map();
    let target_id = move || {
        let id = params.with(|p| p.get("id").cloned().unwrap_or_default());
        urlencoding::decode(&id).unwrap_or(std::borrow::Cow::Borrowed("")).into_owned()
    }; 

    let items_resource = create_resource(
        target_id, 
        move |id| async move { fetch_items(&id).await }
    );

    view! {
        <div class="max-w-7xl mx-auto bg-white p-8 rounded-xl shadow-lg border border-gray-200 mt-8">
            <div class="mb-4">
                    <A href="/" class="text-blue-600 hover:text-blue-800 font-semibold flex items-center gap-1">
                        "← กลับไปหน้าค้นหา"
                    </A>
                </div>
            <h1 class="text-3xl font-bold mb-6 text-blue-900">"ZoomThai: ตารางรายการพัสดุ"</h1>
            
            <Transition fallback=move || view! { 
                <div class="flex items-center justify-center p-12 text-gray-500 font-semibold animate-pulse">
                    "กำลังโหลดข้อมูลจาก API..."
                </div> 
            }>
                {move || items_resource.get().map(|result| match result {
                    Ok(data) => view! {
                        <div>
                            <div class="mb-6 bg-blue-50 p-4 rounded-lg border border-blue-200 flex justify-between items-center">
                                <div>
                                    <p class="font-bold text-gray-800">"รหัสประกาศ (TOR): " <span class="text-blue-700">{data.announcement_id}</span></p>
                                </div>
                                <div class="bg-blue-600 text-white px-4 py-2 rounded-full font-semibold text-sm shadow-sm">
                                    "จำนวนทั้งหมด " {data.total_items} " รายการ"
                                </div>
                            </div>

                            <div class="overflow-x-auto rounded-lg border border-gray-200 shadow-sm">
                                <table class="w-full text-sm text-left">
                                    <thead class="bg-gray-100 text-gray-700 uppercase text-xs font-bold">
                                        <tr>
                                            <th class="px-4 py-3 text-center border-b">"ลำดับ"</th>
                                            <th class="px-4 py-3 border-b">"รหัสพัสดุ"</th>
                                            <th class="px-4 py-3 border-b">"รายละเอียดรายการ"</th>
                                            <th class="px-4 py-3 text-right border-b">"จำนวน"</th>
                                            <th class="px-4 py-3 text-center border-b">"หน่วย"</th>
                                            <th class="px-4 py-3 text-right border-b">"ราคา/หน่วย"</th>
                                            <th class="px-4 py-3 text-right border-b">"ราคารวม (บาท)"</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {data.items.into_iter().map(|item| {
                                            view! {
                                                <tr class="bg-white border-b hover:bg-gray-50 transition-colors">
                                                    <td class="px-4 py-3 text-center text-gray-600 font-medium">
                                                        {item.line_no.unwrap_or_default()}
                                                    </td>
                                                    <td class="px-4 py-3 font-mono text-gray-500">
                                                        {
                                                            let code = item.item_code.unwrap_or_default();
                                                            if code.is_empty() { "-".to_string() } else { code }
                                                        }
                                                    </td>
                                                    <td class="px-4 py-3 font-medium text-gray-800">
                                                        {item.description.unwrap_or_default()}
                                                    </td>
                                                    <td class="px-4 py-3 text-right text-green-700 font-bold">
                                                        {item.quantity.unwrap_or_default()}
                                                    </td>
                                                    <td class="px-4 py-3 text-center text-gray-600">
                                                        {item.unit.unwrap_or_default()}
                                                    </td>
                                                    <td class="px-4 py-3 text-right text-gray-600">
                                                        {item.unit_price_estimate.unwrap_or_default()}
                                                    </td>
                                                    <td class="px-4 py-3 text-right text-blue-700 font-bold">
                                                        {item.total_price_estimate.unwrap_or_default()}
                                                    </td>
                                                </tr>
                                            }
                                        }).collect_view()}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    }.into_view(),
                    
                    Err(e) => view! {
                        <div class="bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded shadow-sm">
                            <p class="font-bold">"เชื่อมต่อ API ล้มเหลว"</p>
                            <p>"โปรดตรวจสอบว่า Backend API ทำงานอยู่ - Error: " {e.to_string()}</p>
                        </div>
                    }.into_view(),
                })}
            </Transition>
        </div>
    }
}