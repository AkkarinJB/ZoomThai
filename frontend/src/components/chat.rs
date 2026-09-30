use leptos::*;
use leptos_router::*;
use crate::models::search::{AskRequest, AskResponse, Citation};
use crate::services::api::ask_question;
use crate::components::ui::{ErrorState, ConfidenceBar};

#[component]
pub fn AskPage() -> impl IntoView {
    let (question, set_question) = create_signal(String::new());
    let (response, set_response) = create_signal::<Option<AskResponse>>(None);
    let (is_loading, set_is_loading) = create_signal(false);
    let (error_msg, set_error_msg) = create_signal::<Option<String>>(None);
    let (latency_ms, set_latency_ms) = create_signal(0.0f64);

    let ask_action = create_action(move |q: &String| {
        let q = q.clone();
        async move {
            set_is_loading.set(true);
            set_error_msg.set(None);
            set_response.set(None);

            let start = js_sys::Date::now();
            let req = AskRequest { question: q, top_k: 5 };

            match ask_question(req).await {
                Ok(data) => {
                    let elapsed = js_sys::Date::now() - start;
                    set_latency_ms.set(elapsed);
                    set_response.set(Some(data));
                }
                Err(e) => set_error_msg.set(Some(e)),
            }
            set_is_loading.set(false);
        }
    });

    let examples = vec![
        "PEA จัดซื้อสายไฟ 22kV มีรายการอะไรบ้าง",
        "วงเงินรวมของรายการพัสดุทั้งหมดเป็นเท่าไร",
        "มีรายการใดที่เกี่ยวกับหม้อแปลงไฟฟ้าบ้าง",
    ];

    view! {
        <div class="page-container max-w-3xl mx-auto">
            <div class="page-header">
                <h1 class="page-title">"ถามตอบด้วย AI"</h1>
                <p class="page-subtitle">
                    "ถามคำถามเกี่ยวกับข้อมูลจัดซื้อจัดจ้าง — ระบบจะค้นหาและสรุปคำตอบจากเอกสาร TOR"
                </p>
            </div>

            // Input form
            <div class="card card-body mb-6">
                <div class="form-group mb-4">
                    <label class="form-label">"คำถามของคุณ"</label>
                    <textarea
                        class="form-textarea"
                        rows="4"
                        placeholder="เช่น PEA ประกาศจัดซื้อสายไฟ 22kV ในปีงบ 2564 มีกี่รายการ และวงเงินรวมเท่าไร?"
                        prop:value=question
                        on:input=move |ev| set_question.set(event_target_value(&ev))
                        disabled=is_loading
                    ></textarea>
                </div>

                <div class="flex flex-wrap gap-2 mb-4">
                    <span class="text-xs text-gray-400 self-center">"ตัวอย่าง:"</span>
                    {examples.into_iter().map(|ex| {
                        let ex_str = ex.to_string();
                        let ex_set = ex_str.clone();
                        view! {
                            <button
                                type="button"
                                class="badge badge-agency-default cursor-pointer hover:bg-purple-50 transition-colors"
                                on:click=move |_| set_question.set(ex_set.clone())
                            >
                                {ex_str}
                            </button>
                        }
                    }).collect_view()}
                </div>

                <div class="flex gap-3">
                    <button
                        class="btn btn-primary flex-1"
                        disabled=move || is_loading.get() || question.get().trim().is_empty()
                        on:click=move |_| {
                            let q = question.get_untracked();
                            if !q.trim().is_empty() {
                                ask_action.dispatch(q);
                            }
                        }
                    >
                        {move || if is_loading.get() { "กำลังประมวลผล..." } else { "ส่งคำถาม" }}
                    </button>
                    {move || {
                        if response.get().is_some() || error_msg.get().is_some() {
                            view! {
                                <button
                                    class="btn btn-secondary"
                                    on:click=move |_| {
                                        set_response.set(None);
                                        set_error_msg.set(None);
                                        set_question.set(String::new());
                                    }
                                >
                                    "ล้าง"
                                </button>
                            }.into_view()
                        } else {
                            view! { <span></span> }.into_view()
                        }
                    }}
                </div>
            </div>

            // Loading state
            {move || {
                if is_loading.get() {
                    view! {
                        <div class="card card-body text-center py-12">
                            <p class="text-4xl mb-3 animate-pulse">"..."</p>
                            <p class="font-semibold text-gray-700">"กำลังค้นหาและประมวลผลคำตอบ..."</p>
                            <p class="text-xs text-gray-400 mt-2">
                                "สร้าง embedding → ค้นหาข้อมูล → สรุปคำตอบ"
                            </p>
                        </div>
                    }.into_view()
                } else {
                    view! { <span></span> }.into_view()
                }
            }}

            // Error state
            {move || {
                error_msg.get().map(|err| {
                    let retry = Callback::new(move |_: ()| {
                        let q = question.get_untracked();
                        if !q.is_empty() { ask_action.dispatch(q); }
                    });
                    view! {
                        <div class="mb-6">
                            <ErrorState message=err on_retry=retry />
                        </div>
                    }
                })
            }}

            // Answer area
            {move || {
                response.get().map(|data| {
                    let has_answer = data.answer.as_ref()
                        .map(|a| !a.trim().is_empty())
                        .unwrap_or(false);
                    let unable = data.unable_reason.clone();
                    let is_insufficient = unable.as_deref()
                        .map(|r| r == "NO_CONTEXT" || r == "EMBEDDING_ERROR")
                        .unwrap_or(false);

                    view! {
                        <div class="space-y-4">
                            // Meta bar
                            <div class="card card-body py-3 flex items-center justify-between gap-6">
                                {data.confidence.map(|c| view! { <ConfidenceBar value=c /> })}
                                <div class="flex items-center gap-2">
                                    <span class="text-xs text-gray-400">"ใช้เวลา"</span>
                                    <span class="text-sm font-semibold text-gray-600 font-mono">
                                        {format!("{:.0}ms", latency_ms.get())}
                                    </span>
                                </div>
                            </div>

                            // Answer box
                            <div class="card card-body">
                                <h3 class="card-title mb-3 flex items-center gap-2">
                                    "คำตอบ"
                                </h3>
                                {if is_insufficient || !has_answer {
                                    view! {
                                        <div class="alert alert-warning">
                                            <p class="alert-title">"ไม่พบข้อมูลเพียงพอ"</p>
                                            <p class="text-sm mt-1">
                                                "ระบบไม่พบข้อมูลที่เกี่ยวข้องในฐานข้อมูลเพียงพอที่จะตอบคำถามนี้ได้"
                                            </p>
                                        </div>
                                    }.into_view()
                                } else {
                                    view! {
                                        <div class="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap bg-gray-50 rounded-xl p-4 border border-gray-100">
                                            {data.answer.clone().unwrap_or_default()}
                                        </div>
                                    }.into_view()
                                }}
                            </div>

                            // Citations
                            {data.citations.clone().filter(|c| !c.is_empty()).map(|citations| view! {
                                <div class="card card-body">
                                    <h3 class="card-title mb-3">"แหล่งอ้างอิง"</h3>
                                    <div class="space-y-3">
                                        {citations.into_iter().enumerate().map(|(i, cite)| view! {
                                            <CitationCard index=i+1 citation=cite />
                                        }).collect_view()}
                                    </div>
                                </div>
                            })}
                        </div>
                    }.into_view()
                })
            }}
        </div>
    }
}

#[component]
fn CitationCard(index: usize, citation: Citation) -> impl IntoView {
    let ctx = use_context::<RwSignal<Option<crate::models::search::Announcement>>>();
    let navigate = use_navigate();
    let id = citation.announcement_id.clone();
    let encoded = urlencoding::encode(&id).to_string();
    let enc_nav = encoded.clone();

    view! {
        <div class="citation-card flex items-start justify-between gap-3">
            <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                    <span class="citation-index">{index.to_string()}</span>
                    <span class="citation-id">{citation.announcement_id.clone()}</span>
                    <span class="text-xs text-gray-400">
                        "หน้า " {citation.page_number.to_string()}
                    </span>
                </div>
                <p class="citation-snippet pl-7">
                    "\"" {citation.text_snippet.clone()} "\""
                </p>
            </div>
            <button
                class="btn btn-secondary btn-xs shrink-0"
                on:click=move |_| {
                    let _ = ctx;
                    navigate(&format!("/announcements/{}", enc_nav), Default::default());
                }
            >
                "ดูรายละเอียด"
            </button>
        </div>
    }
}