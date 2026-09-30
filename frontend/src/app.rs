use leptos::*;
use leptos_router::*;
use crate::components::home::Home;
use crate::components::procurement_table::ProcurementTable;

#[component]
pub fn App() -> impl IntoView {
    view! {
        <Router>
            <main class="min-h-screen bg-gray-100">
                <Routes>
                    <Route path="/" view=Home />
                    <Route path="/announcements/*id" view=ProcurementTable />
                </Routes>
            </main>
        </Router>
    }
}