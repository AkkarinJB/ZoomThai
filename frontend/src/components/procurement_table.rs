use leptos::*;
use leptos_router::*;
use crate::config::{ITEM_COLUMNS, SIMILAR_LIMIT, SIMILAR_TITLE_WORDS};
use crate::models::procurement::ProcurementItem;
use crate::models::search::{Announcement, SearchRequest, SearchResponse};
use crate::services::api::{fetch_items, search_announcements};
use crate::components::ui::{
    AgencyBadge, MethodBadge, FiscalYearBadge,
    LoadingState, InlineLoading, EmptyState, ErrorState,
};


#[component]
pub fn DetailPage() -> impl IntoView {
    let params    = use_params_map();
    let target_id = move || {
        let raw = params.with(|p| p.get("id").cloned().unwrap_or_default());
        urlencoding::decode(&raw).unwrap_or_default().into_owned()
    };

    let ctx      = use_context::<RwSignal<Option<Announcement>>>();
    let selected = move || ctx.and_then(|c| c.get());

    let (sort_col, set_sort_col) = create_signal("line_no".to_string());
    let (sort_asc, set_sort_asc) = create_signal(true);

    let toggle_sort = move |col: &str| {
        let col = col.to_string();
        if sort_col.get_untracked() == col {
            set_sort_asc.update(|v| *v = !*v);
        } else {
            set_sort_col.set(col);
            set_sort_asc.set(true);
        }
    };

    let items_resource = create_resource(target_id, |id| async move {
        fetch_items(&id).await
    });

    let sorted_items = create_memo(move |_| {
        items_resource
            .get()
            .and_then(|r| r.ok())
            .map(|data| {
                let mut items = data.items.clone();
                let col = sort_col.get();
                let asc = sort_asc.get();
                items.sort_by(|a, b| {
                    let ord = match col.as_str() {
                        "description" => a.description.cmp(&b.description),
                        "quantity"    => cmp_numeric(&a.quantity, &b.quantity),
                        "unit_price"  => cmp_numeric(&a.unit_price_estimate, &b.unit_price_estimate),
                        "total_price" => cmp_numeric(&a.total_price_estimate, &b.total_price_estimate),
                        _             => a.line_no.cmp(&b.line_no),
                    };
                    if asc { ord } else { ord.reverse() }
                });
                items
            })
    });

    let title_source = create_memo(move |_| {
        selected().map(|a| {
            a.title.split_whitespace().take(SIMILAR_TITLE_WORDS).collect::<Vec<_>>().join(" ")
        })
    });

    let similar_resource = create_resource(
        move || title_source.get(),
        |title_opt| async move {
            match title_opt {
                None    => Ok(SearchResponse::default()),
                Some(q) => search_announcements(SearchRequest {
                    query: q,
                    filters: None,
                    limit: (SIMILAR_LIMIT + 1) as i32, 
                    offset: 0,
                }).await,
            }
        },
    );

    view! {
        <div class="page-container max-w-6xl mx-auto space-y-6">
            <A href="/" class="btn btn-ghost btn-sm inline-flex">
                "Prev  กลับไปหน้าค้นหา"
            </A>

            // Announcement header
            {move || {
                let id  = target_id();
                let ann = selected();
                view! {
                    <div class="card card-body">
                        <div class="flex items-start justify-between gap-4 flex-wrap">
                            <div class="flex-1 min-w-0">
                                {ann.as_ref().map(|a| view! {
                                    <div class="flex flex-wrap items-center gap-2 mb-3">
                                        <AgencyBadge agency=a.agency.clone() />
                                        {a.method.clone().map(|m| view! { <MethodBadge method=m /> })}
                                        {a.fiscal_year.map(|y| view! { <FiscalYearBadge year=y /> })}
                                    </div>
                                })}
                                <h1 class="text-xl font-bold text-gray-900 leading-snug max-w-2xl">
                                    {ann.as_ref().map(|a| a.title.clone()).unwrap_or_else(|| "ข้อมูลประกาศ".to_string())}
                                </h1>
                                <p class="result-id mt-2">{id}</p>
                            </div>

                            {ann.as_ref().map(|a| view! {
                                <div class="text-right space-y-2 shrink-0">
                                    {a.budget_amount.clone().map(|b| view! {
                                        <div>
                                            <p class="text-xs text-gray-400">"วงเงิน"</p>
                                            <p class="text-2xl font-extrabold text-purple-700">"฿" {b}</p>
                                        </div>
                                    })}
                                    {a.submission_deadline.clone().map(|d| view! {
                                        <div>
                                            <p class="text-xs text-gray-400">"กำหนดรับเอกสาร"</p>
                                            <p class="text-sm font-semibold text-orange-600">
                                                {d.get(..10).unwrap_or(&d).to_string()}
                                            </p>
                                        </div>
                                    })}
                                </div>
                            })}
                        </div>

                        {move || selected()
                            .and_then(|a| a.tor_pdf_path)
                            .map(|path| view! {
                                <div class="mt-4 pt-4 border-t border-gray-100">
                                    <a
                                        href={path}
                                        target="_blank"
                                        rel="noopener noreferrer"
                                        class="btn btn-danger"
                                    >
                                        "ดู TOR ต้นฉบับ (PDF)"
                                    </a>
                                </div>
                            })
                        }
                    </div>
                }.into_view()
            }}

            // Items table
            <div class="card overflow-hidden">
                <div class="card-header">
                    <h2 class="card-title">"ตารางรายการพัสดุ"</h2>
                    <Transition fallback=move || view! { <InlineLoading /> }>
                        {move || items_resource.get()
                            .and_then(|r| r.ok())
                            .map(|d| view! {
                                <span class="text-sm text-gray-500">
                                    "ทั้งหมด "
                                    <span class="font-bold text-purple-700">{d.total_items}</span>
                                    " รายการ"
                                </span>
                            })
                        }
                    </Transition>
                </div>

                <Transition fallback=move || view! { <LoadingState message="กำลังโหลดรายการ..." /> }>
                    {move || match items_resource.get() {
                        None          => view! { <div></div> }.into_view(),
                        Some(Err(e))  => view! { <ErrorState message=e /> }.into_view(),
                        Some(Ok(_))   => {
                            let items = sorted_items.get().unwrap_or_default();
                            let sc    = sort_col;
                            let sa    = sort_asc;

                            let sort_ind = move |field: &'static str| {
                                move || if sc.get() == field {
                                    if sa.get() { " [asc]" } else { " [desc]" }
                                } else { "" }
                            };

                            view! {
                                <div class="overflow-x-auto">
                                    <table class="data-table">
                                        <thead>
                                            <tr>
                                                {ITEM_COLUMNS.iter().map(|col| {
                                                    let field     = col.field;
                                                    let th_align  = col.align.th_class();
                                                    let sortable  = col.sortable;
                                                    let th_class  = if sortable {
                                                        format!("th-sortable {}", th_align)
                                                    } else {
                                                        th_align.to_string()
                                                    };
                                                    view! {
                                                        <th
                                                            class={th_class}
                                                            on:click=move |_| {
                                                                if sortable { toggle_sort(field) }
                                                            }
                                                        >
                                                            {col.label}
                                                            {if sortable {
                                                                view! {
                                                                    <span class="sort-indicator">
                                                                        {sort_ind(field)}
                                                                    </span>
                                                                }.into_view()
                                                            } else {
                                                                view! { <span></span> }.into_view()
                                                            }}
                                                        </th>
                                                    }
                                                }).collect_view()}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {if items.is_empty() {
                                                view! {
                                                    <tr>
                                                        <td colspan="7" class="py-12 text-center text-gray-400">
                                                            "ไม่มีรายการพัสดุ"
                                                        </td>
                                                    </tr>
                                                }.into_view()
                                            } else {
                                                items.into_iter().map(|item| view! {
                                                    <ItemRow item=item />
                                                }).collect_view()
                                            }}
                                        </tbody>
                                    </table>
                                </div>
                            }.into_view()
                        }
                    }}
                </Transition>
            </div>

            // Similar Announcements
            <div class="card card-body">
                <h2 class="card-title mb-4">"ประกาศที่คล้ายกัน"</h2>
                <Transition fallback=move || view! { <InlineLoading message="กำลังค้นหา..." /> }>
                    {move || {
                        let current_id = target_id();
                        if title_source.get().is_none() {
                            return view! {
                                <p class="text-sm text-gray-400 italic">
                                    "(เปิดผ่านหน้าค้นหาเพื่อแสดงประกาศที่คล้ายกัน)"
                                </p>
                            }.into_view();
                        }
                        match similar_resource.get() {
                            None          => view! { <InlineLoading /> }.into_view(),
                            Some(Err(e))  => view! { <ErrorState message=e /> }.into_view(),
                            Some(Ok(data)) => {
                                let items: Vec<_> = data.items.into_iter()
                                    .filter(|a| a.id != current_id)
                                    .take(SIMILAR_LIMIT)
                                    .collect();

                                if items.is_empty() {
                                    view! {
                                        <EmptyState heading="ไม่พบประกาศที่คล้ายกัน" />
                                    }.into_view()
                                } else {
                                    view! {
                                        <div class="space-y-2">
                                            {items.into_iter().map(|a| view! {
                                                <SimilarCard item=a />
                                            }).collect_view()}
                                        </div>
                                    }.into_view()
                                }
                            }
                        }
                    }}
                </Transition>
            </div>
        </div>
    }
}


#[component]
fn ItemRow(item: ProcurementItem) -> impl IntoView {
    let empty = || "-".to_string();
    view! {
        <tr>
            <td class="col-center col-mono col-muted">
                {item.line_no.map(|n| n.to_string()).unwrap_or_else(empty)}
            </td>
            <td class="col-mono col-muted">
                {item.item_code.filter(|s| !s.is_empty()).unwrap_or_else(empty)}
            </td>
            <td>{item.description.unwrap_or_default()}</td>
            <td class="col-right col-mono">{item.quantity.unwrap_or_default()}</td>
            <td class="col-center col-muted">{item.unit.unwrap_or_default()}</td>
            <td class="col-right col-mono">{item.unit_price_estimate.unwrap_or_default()}</td>
            <td class="col-right col-mono col-accent">{item.total_price_estimate.unwrap_or_default()}</td>
        </tr>
    }
}


#[component]
fn SimilarCard(item: Announcement) -> impl IntoView {
    let ctx      = use_context::<RwSignal<Option<Announcement>>>();
    let navigate = use_navigate();
    let encoded  = urlencoding::encode(&item.id).to_string();
    let item_ctx = item.clone();
    let enc_nav  = encoded.clone();

    view! {
        <div
            class="card-interactive result-card"
            on:click=move |_| {
                if let Some(ctx) = ctx { ctx.set(Some(item_ctx.clone())); }
                navigate(&format!("/announcements/{}", enc_nav), Default::default());
            }
        >
            <div class="flex items-center justify-between">
                <div class="flex-1 min-w-0">
                    <p class="result-title truncate">{item.title.clone()}</p>
                    <p class="result-id">{item.id.clone()}</p>
                </div>
                <AgencyBadge agency=item.agency.clone() />
            </div>
        </div>
    }
}


//  Helpers
fn cmp_numeric(a: &Option<String>, b: &Option<String>) -> std::cmp::Ordering {
    let fa = a.as_deref().and_then(|v| v.parse::<f64>().ok()).unwrap_or(0.0);
    let fb = b.as_deref().and_then(|v| v.parse::<f64>().ok()).unwrap_or(0.0);
    fa.partial_cmp(&fb).unwrap_or(std::cmp::Ordering::Equal)
}