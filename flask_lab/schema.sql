DROP TABLE IF EXISTS settings;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS client;
DROP TABLE IF EXISTS ticket;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS brand;

CREATE TABLE settings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  language VARCHAR DEFAULT 'en',
  refresh INTEGER DEFAULT 60,
  min_role_to_view_board INTEGER DEFAULT 1,
  min_role_to_add INTEGER DEFAULT 1,
  min_role_to_delete INTEGER DEFAULT 2,
  min_role_to_manage_users INTEGER DEFAULT 2,
  min_role_to_manage_settings INTEGER DEFAULT 2
);

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username VARCHAR UNIQUE NOT NULL,
  view_name VARCHAR DEFAULT '',
  role INTEGER DEFAULT 0,
  email VARCHAR,
  status INTEGER DEFAULT 0,
  language VARCHAR DEFAULT 'en',
  password TEXT NOT NULL
);

CREATE TABLE client (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  phone VARCHAR UNIQUE,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  name VARCHAR DEFAULT '',
  email VARCHAR  DEFAULT '',
  last_ticket_id INTEGER,
  language VARCHAR DEFAULT 'en',
  FOREIGN KEY (last_ticket_id) REFERENCES ticket (id)
);

CREATE TABLE ticket (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  client_id VARCHAR,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  title TEXT DEFAULT '',
  body TEXT DEFAULT '',
  pc_kind INTEGER DEFAULT 0,
  pc_manufacturer INTEGER DEFAULT 0,
  pc_model VARCHAR DEFAULT '',
  pc_color INTEGER DEFAULT 0,
  pc_screen_inch VARCHAR DEFAULT 10,
  with_power_supply INTEGER DEFAULT 0,
  pc_login_password TEXT DEFAULT '',
  cpu_diag TEXT DEFAULT 'i7-12000 not stressed temperature 45, stressed 80',
  ram_diag TEXT DEFAULT '16gb ok',
  disk_diag TEXT DEFAULT '256gb ok',
  video_card_diag TEXT DEFAULT '3070Ti stressed temperature 45, stressed 80',
  total_diag TEXT DEFAULT '',
  diagnostic_end TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  recived_by_client TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  spend_time_minutes INTEGER DEFAULT 0,
  spend_parts TEXT DEFAULT '',
  price INTEGER DEFAULT 0,
  status INTEGER DEFAULT 0,
  priority INTEGER DEFAULT 0,
  FOREIGN KEY (author_id) REFERENCES user (id),
  FOREIGN KEY (client_id) REFERENCES client (phone)
);

CREATE TABLE product (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name VARCHAR DEFAULT '',
  brand INTEGER NOT NULL,
  created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  description TEXT DEFAULT '',
  short_description TEXT DEFAULT '',
  price REAL DEFAULT 0.0,
  status INTEGER DEFAULT 0,
  priority INTEGER DEFAULT 0,
  FOREIGN KEY (brand) REFERENCES brand (id)
);

CREATE TABLE brand (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            name VARCHAR DEFAULT '',
            image TEXT DEFAULT '',
            description TEXT DEFAULT '',
            status INTEGER DEFAULT 0,
            priority INTEGER DEFAULT 0
);