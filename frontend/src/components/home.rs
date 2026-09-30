use leptos::*;
use leptos_router::*;
use crate::config::{AGENCIES, METHODS, PAGE_SIZE};
use crate::models::search::{Announcement, SearchFilters, SearchRequest, SearchResponse};
use crate::services::api::search_announcements;
use crate::components::ui::{
    AgencyBadge, MethodBadge, FiscalYearBadge,
    LoadingState, EmptyState, ErrorState,
    Pagination, ResultSummary,
};


#[component]
pub fn SearchPage() -> impl IntoView {
    let (query, set_query)             = create_signal(String::new());
    let (agencies, set_agencies)       = create_signal::<Vec<String>>(vec![]);
    let (budget_min, set_budget_min)   = create_signal(String::new());
    let (budget_max, set_budget_max)   = create_signal(String::new());
    let (method, set_method)           = create_signal(String::new());
    let (response, set_response)       = create_signal::<Option<SearchResponse>>(None);
    let (current_page, set_page)       = create_signal(0i32);
    let (is_loading, set_loading)      = create_signal(false);
    let (error, set_error)             = create_signal::<Option<String>>(None);

    let toggle_agency = move |id: String| {
        set_agencies.update(|v| {
            match v.iter().position(|a| *a == id) {
                Some(i) => { v.remove(i); }
                None    => { v.push(id); }
            }
        });
    };

    let do_search = create_action(move |page: &i32| {
        let page   = *page;
        let q      = query.get_untracked();
        let ag     = agencies.get_untracked();
        let bmin   = budget_min.get_untracked().parse::<f64>().ok();
        let bmax   = budget_max.get_untracked().parse::<f64>().ok();
        let mval   = method.get_untracked();
        let meth   = if mval.is_empty() { None } else { Some(mval) };

        async move {
            set_loading.set(true);
            set_error.set(None);
            set_page.set(page);

            let has_filters = !ag.is_empty() || bmin.is_some() || bmax.is_some() || meth.is_some();
            let filters = has_filters.then(|| SearchFilters {
                agency: ag,
                budget_min: bmin,
                budget_max: bmax,
                method: meth,
            });

            let q_safe = if q.trim().is_empty() { " ".to_string() } else { q };
            let req = SearchRequest { query: q_safe, filters, limit: PAGE_SIZE, offset: page * PAGE_SIZE };

            match search_announcements(req).await {
                Ok(data)  => set_response.set(Some(data)),
                Err(msg)  => set_error.set(Some(msg)),
            }
            set_loading.set(false);
        }
    });

    let on_prev = Callback::new(move |_: ()| do_search.dispatch(current_page.get_untracked() - 1));
    let on_next = Callback::new(move |_: ()| do_search.dispatch(current_page.get_untracked() + 1));

    view! {
        <div class="page-container max-w-5xl mx-auto">
            <div class="page-header">
                <h1 class="page-title">"ค้นหาประกาศจัดซื้อจัดจ้าง"</h1>
            </div>

            // Search form
            <form
                class="card card-body mb-6"
                on:submit=move |ev| { ev.prevent_default(); do_search.dispatch(0); }
            >
                <div class="flex gap-3 mb-5">
                    <input
                        type="text"
                        class="form-input form-input-lg flex-1"
                        placeholder="เช่น สายไฟ 22kV, หม้อแปลง, ท่อ HDPE..."
                        prop:value=query
                        on:input=move |ev| set_query.set(event_target_value(&ev))
                    />
                    <button type="submit" class="btn btn-primary btn-lg" disabled=is_loading>
                        {move || if is_loading.get() { "กำลังค้นหา..." } else { "ค้นหา" }}
                    </button>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-5 border-t border-gray-100 pt-4">
                    <div class="form-group">
                        <label class="form-label">"หน่วยงาน"</label>
                        <div class="flex flex-wrap gap-x-4 gap-y-2">
                            {AGENCIES.iter().map(|cfg| {
                                let id       = cfg.id.to_string();
                                let label    = cfg.label.to_string();
                                let id_check = id.clone();
                                view! {
                                    <label class="flex items-center gap-1.5 text-sm cursor-pointer select-none">
                                        <input
                                            type="checkbox"
                                            class="form-checkbox"
                                            on:change=move |_| toggle_agency(id_check.clone())
                                        />
                                        <span class="text-gray-700">{label}</span>
                                    </label>
                                }
                            }).collect_view()}
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">"งบประมาณ (บาท)"</label>
                        <div class="flex items-center gap-2">
                            <input type="number" class="form-input" placeholder="ขั้นต่ำ"
                                prop:value=budget_min
                                on:input=move |ev| set_budget_min.set(event_target_value(&ev))
                            />
                            <span class="text-gray-300 shrink-0">"–"</span>
                            <input type="number" class="form-input" placeholder="สูงสุด"
                                prop:value=budget_max
                                on:input=move |ev| set_budget_max.set(event_target_value(&ev))
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">"วิธีจัดซื้อ"</label>
                        <select class="form-select" on:change=move |ev| set_method.set(event_target_value(&ev))>
                            <option value="">"ทั้งหมด"</option>
                            {METHODS.iter().map(|cfg| view! {
                                <option value={cfg.id}>{cfg.label}</option>
                            }).collect_view()}
                        </select>
                    </div>
                </div>
            </form>

            // Results — reactive block, ทุก state แยกชัดเจน
            {move || {
                if is_loading.get() {
                    view! { <LoadingState message="กำลังดึงข้อมูล..." /> }.into_view()
                } else if let Some(err) = error.get() {
                    let retry = Callback::new(move |_: ()| do_search.dispatch(current_page.get_untracked()));
                    view! { <ErrorState message=err on_retry=retry /> }.into_view()
                } else if let Some(data) = response.get() {
                    let total       = data.total;
                    let latency     = data.query_time_ms;
                    let items       = data.items.clone();
                    let total_pages = (total + PAGE_SIZE - 1) / PAGE_SIZE;

                    if items.is_empty() {
                        view! {
                            <EmptyState
                                heading="ไม่พบข้อมูลที่ตรงกัน"
                                sub="ลองปรับคำค้นหาหรือเปลี่ยนตัวกรอง"
                            />
                        }.into_view()
                    } else {
                        view! {
                            <div>
                                <ResultSummary total=total latency_ms=latency />
                                <div class="space-y-3">
                                    {items.into_iter().map(|item| view! {
                                        <AnnouncementCard item=item />
                                    }).collect_view()}
                                </div>
                                {if total_pages > 1 {
                                    view! {
                                        <Pagination
                                            current_page=current_page
                                            total_pages=total_pages
                                            on_prev=on_prev
                                            on_next=on_next
                                        />
                                    }.into_view()
                                } else {
                                    view! { <span></span> }.into_view()
                                }}
                            </div>
                        }.into_view()
                    }
                } else {
                    view! {
                        <EmptyState heading="กรอกคำค้นหาแล้วกดปุ่ม ค้นหา เพื่อเริ่มต้น" />
                    }.into_view()
                }
            }}
        </div>
    }
}


#[component]
fn AnnouncementCard(item: Announcement) -> impl IntoView {
    let ctx      = use_context::<RwSignal<Option<Announcement>>>();
    let navigate = use_navigate();
    let encoded  = urlencoding::encode(&item.id).to_string();
    let item_ctx = item.clone();
    let enc_nav  = encoded.clone();

    let on_click = move |_: leptos::ev::MouseEvent| {
        if let Some(ctx) = ctx { ctx.set(Some(item_ctx.clone())); }
        navigate(&format!("/announcements/{}", enc_nav), Default::default());
    };

    let budget   = item.budget_amount.as_deref().map(|b| format!("฿{}", b)).unwrap_or_else(|| "ไม่ระบุ".into());
    let deadline = item.submission_deadline.as_deref().and_then(|d| d.get(..10)).unwrap_or("ไม่ระบุ").to_string();

    view! {
        <div class="result-card" on:click=on_click style="cursor: pointer;">
            <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                    <div class="flex flex-wrap items-center gap-2 mb-2">
                        <AgencyBadge agency=item.agency.clone() />
                        {item.method.clone().map(|m| view! { <MethodBadge method=m /> })}
                        {item.fiscal_year.map(|y| view! { <FiscalYearBadge year=y /> })}
                    </div>
                    <p class="result-title">{item.title.clone()}</p>
                    <p class="result-id">{item.id.clone()}</p>
                </div>
                <div class="text-right shrink-0 flex flex-col items-end gap-2">
                    <div>
                        <p class="font-bold text-purple-700 text-sm">{budget}</p>
                        <p class="result-meta">"ปิดรับ: " {deadline}</p>
                    </div>
                    <button class="btn btn-primary btn-xs">
                        "ดูรายละเอียด"
                    </button>
                </div>
            </div>
        </div>
    }
}