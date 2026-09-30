use leptos::*;
use leptos_router::*;
use crate::models::search::Announcement;
use crate::components::home::SearchPage;
use crate::components::procurement_table::DetailPage;
use crate::components::chat::AskPage;

#[component]
pub fn App() -> impl IntoView {
    let selected: RwSignal<Option<Announcement>> = create_rw_signal(None);
    provide_context(selected);

    view! {
        <Router>
            <nav class="navbar">
                <div class="navbar-inner">
                    <A href="/" class="navbar-brand">
                        "ZoomThai"
                    </A>
                    <div class="navbar-links">
                        <A href="/" class="navbar-link" exact=true active_class="navbar-link-active">
                            "ค้นหา"
                        </A>
                        <A href="/ask" class="navbar-link" exact=true active_class="navbar-link-active">
                            "ถามตอบ AI"
                        </A>
                    </div>
                </div>
            </nav>

            <main>
                <Routes>
                    <Route path="/"                    view=SearchPage  />
                    <Route path="/announcements/:id"   view=DetailPage  />
                    <Route path="/ask"                 view=AskPage     />
                </Routes>
            </main>
        </Router>
    }
}