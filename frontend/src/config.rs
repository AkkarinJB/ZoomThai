pub const PAGE_SIZE: i32 = 10;
pub const SIMILAR_LIMIT: usize = 3;
pub const SIMILAR_TITLE_WORDS: usize = 5;

pub struct AgencyConfig {
    pub id: &'static str,
    pub label: &'static str,
    pub badge_class: &'static str,
}

pub const AGENCIES: &[AgencyConfig] = &[
    AgencyConfig { id: "PEA",   label: "PEA",   badge_class: "badge badge-agency-pea"     },
    AgencyConfig { id: "EGAT",  label: "EGAT",  badge_class: "badge badge-agency-egat"    },
    AgencyConfig { id: "MEA",   label: "MEA",   badge_class: "badge badge-agency-mea"     },
    AgencyConfig { id: "e-GP",  label: "e-GP",  badge_class: "badge badge-agency-default" },
    AgencyConfig { id: "กทม.", label: "กทม.", badge_class: "badge badge-agency-default" },
];

pub fn agency_badge_class(agency: &str) -> &'static str {
    AGENCIES
        .iter()
        .find(|a| a.id == agency)
        .map(|a| a.badge_class)
        .unwrap_or("badge badge-agency-default")
}


pub struct MethodConfig {
    pub id: &'static str,
    pub label: &'static str,
}

pub const METHODS: &[MethodConfig] = &[
    MethodConfig { id: "e-bidding",     label: "e-Bidding"     },
    MethodConfig { id: "สอบราคา",      label: "สอบราคา"      },
    MethodConfig { id: "คัดเลือก",     label: "คัดเลือก"     },
    MethodConfig { id: "เฉพาะเจาะจง", label: "เฉพาะเจาะจง" },
];

pub struct ColumnConfig {
    pub field: &'static str,
    pub label: &'static str,
    pub align: ColumnAlign,
    pub sortable: bool,
}

pub enum ColumnAlign {
    Left,
    Right,
    Center,
}

impl ColumnAlign {
    pub fn th_class(&self) -> &'static str {
        match self {
            Self::Left   => "",
            Self::Right  => "col-right",
            Self::Center => "col-center",
        }
    }

    pub fn td_class(&self) -> &'static str {
        match self {
            Self::Left   => "",
            Self::Right  => "col-right col-mono",
            Self::Center => "col-center col-mono",
        }
    }
}

pub const ITEM_COLUMNS: &[ColumnConfig] = &[
    ColumnConfig { field: "line_no",      label: "ลำดับ",          align: ColumnAlign::Center, sortable: true  },
    ColumnConfig { field: "item_code",    label: "รหัสพัสดุ",      align: ColumnAlign::Left,   sortable: false },
    ColumnConfig { field: "description",  label: "รายละเอียด",     align: ColumnAlign::Left,   sortable: true  },
    ColumnConfig { field: "quantity",     label: "จำนวน",          align: ColumnAlign::Right,  sortable: true  },
    ColumnConfig { field: "unit",         label: "หน่วย",          align: ColumnAlign::Center, sortable: false },
    ColumnConfig { field: "unit_price",   label: "ราคา/หน่วย",    align: ColumnAlign::Right,  sortable: true  },
    ColumnConfig { field: "total_price",  label: "ราคารวม (บาท)", align: ColumnAlign::Right,  sortable: true  },
];
