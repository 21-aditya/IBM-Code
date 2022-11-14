CREATE TABLE IF NOT EXISTS imagetable (
    id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY,
    photo blob NOT NULL,
    pred VARCHAR(50),
    date_entry TIMESTAMP DEFAULT CURRENT_TIMESTAMP 
) ENGINE=InnoDB DEFAULT CHARSET=utf8;