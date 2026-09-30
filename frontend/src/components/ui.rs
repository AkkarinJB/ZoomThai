use leptos::*;

#[component]
pub fn AgencyBadge(agency: String) -> impl IntoView {
    let cls = crate::config::agency_badge_class(&agency);
    view! { <span class={cls}>{agency}</span> }
}

#[component]
pub fn MethodBadge(method: String) -> impl IntoView {
    view! { <span class="badge badge-method">{method}</span> }
}

#[component]
pub fn FiscalYearBadge(year: i32) -> impl IntoView {
    view! {
        <span class="badge badge-fiscal">
            "ปีงบ " {year.to_string()}
        </span>
    }
}


#[component]
pub fn LoadingState(
    #[prop(default = "กำลังโหลด...")] message: &'static str,
) -> impl IntoView {
    view! {
        <div class="state-container">
            <div class="spinner"></div>
            <p class="state-sub">{message}</p>
        </div>
    }
}

#[component]
pub fn InlineLoading(
    #[prop(default = "กำลังโหลด...")] message: &'static str,
) -> impl IntoView {
    view! {
        <span class="text-sm text-gray-400 flex items-center gap-2">
            <span class="inline-block w-4 h-4 border-2 border-gray-200 border-t-purple-500 rounded-full animate-spin"></span>
            {message}
        </span>
    }
}


#[component]
pub fn EmptyState(
    heading: &'static str,
    #[prop(optional)] sub: Option<&'static str>,
) -> impl IntoView {
    view! {
        <div class="state-container">
            <p class="state-heading">{heading}</p>
            {sub.map(|s| view! { <p class="state-sub">{s}</p> })}
        </div>
    }
}


#[component]
pub fn ErrorState(
    message: String,
    #[prop(optional)] on_retry: Option<Callback<()>>,
) -> impl IntoView {
    view! {
        <div class="alert alert-error">
            <p class="alert-title">"ไม่สามารถเชื่อมต่อได้"</p>
            <p class="text-sm mb-3">{message}</p>
            {on_retry.map(|retry| view! {
                <button
                    class="btn btn-danger btn-sm"
                    on:click=move |_| retry.call(())
                >
                    "ลองอีกครั้ง"
                </button>
            })}
        </div>
    }
}


#[component]
pub fn ConfidenceBar(value: f64) -> impl IntoView {
    let pct = (value * 100.0).round() as i32;
    let fill_class = if pct >= 80 {
        "confidence-fill confidence-high"
    } else if pct >= 60 {
        "confidence-fill confidence-medium"
    } else {
        "confidence-fill confidence-low"
    };

    view! {
        <div class="confidence-bar">
            <span class="text-xs text-gray-500">"ความมั่นใจ"</span>
            <div class="confidence-track">
                <div
                    class={fill_class}
                    style={format!("width: {}%", pct)}
                ></div>
            </div>
            <span class="confidence-label">{format!("{}%", pct)}</span>
        </div>
    }
}


#[component]
pub fn Pagination(
    current_page: ReadSignal<i32>,
    total_pages: i32,
    on_prev: Callback<()>,
    on_next: Callback<()>,
) -> impl IntoView {
    view! {
        <div class="pagination">
            <button
                class="btn btn-secondary btn-sm"
                disabled=move || current_page.get() == 0
                on:click=move |_| on_prev.call(())
            >
                "Prev"
            </button>
            <span class="pagination-info">
                "หน้า " {move || current_page.get() + 1} " / " {total_pages}
            </span>
            <button
                class="btn btn-secondary btn-sm"
                disabled=move || current_page.get() >= total_pages - 1
                on:click=move |_| on_next.call(())
            >
                "Next"
            </button>
        </div>
    }
}


#[component]
pub fn ResultSummary(total: i32, latency_ms: f64) -> impl IntoView {
    view! {
        <p class="text-sm text-gray-500 mb-4">
            "พบ "
            <span class="font-bold text-purple-700">{total}</span>
            " รายการ | ใช้เวลา "
            <span class="font-mono text-gray-600">{format!("{:.0}ms", latency_ms)}</span>
        </p>
    }
}
