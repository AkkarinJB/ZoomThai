pub mod config;
pub mod environments;
pub mod models;
pub mod services;
pub mod components;

mod app;

use leptos::*;
use app::App;

fn main() {
    console_error_panic_hook::set_once();
    mount_to_body(|| view! { <App/> })
}