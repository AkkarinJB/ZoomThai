pub mod dev;
pub mod prod;

pub struct Environment {
    pub api_base_url: &'static str,
}

#[cfg(debug_assertions)]
pub use dev::ENV;

#[cfg(not(debug_assertions))]
pub use prod::ENV;