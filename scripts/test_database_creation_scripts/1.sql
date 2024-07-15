INSERT INTO merchants (id, name, online, rule) VALUES (1, 'Penn Station', 0, 'pennstation');
INSERT INTO merchants (id, name, online, rule) VALUES (2, 'Outback Steak House', 0, 'outbackhouse');
INSERT INTO merchants (id, name, online, rule) VALUES (3, 'Amazon', 1, 'amazon');
INSERT INTO merchants (id, name, online, rule) VALUES (4, 'Apple', 0, null);
INSERT INTO merchants (id, name, online, rule) VALUES (5, 'Port City Java', 0, null);
INSERT INTO merchants (id, name, online, rule) VALUES (6, 'BJS', 0, 'bjsrewards');
INSERT INTO merchants (id, name, online, rule) VALUES (7, 'Dollar General', 0, 'dollar_general');
INSERT INTO merchants (id, name, online, rule) VALUES (8, 'Bambu Labs', 1, 'bambu');
INSERT INTO merchants (id, name, online, rule) VALUES (9, 'Etsy', 1, 'etsy');

INSERT INTO locations (id, description, merchant_id, lat, long) VALUES (1, 'Falls of Neuse', 1, 35.86837825457926, -78.62150981593383);
INSERT INTO locations (id, description, merchant_id, lat, long) VALUES (2, 'Capital', 2, 35.85665622223983, -78.58032796673776);
INSERT INTO locations (id, description, merchant_id, lat, long) VALUES (3, 'Crabtree Mall', 4, 35.8408590921226, -78.68011850195218);
INSERT INTO locations (id, description, merchant_id, lat, long) VALUES (4, 'EB2', 5, 35.77184197261896, -78.67356047898443);
INSERT INTO locations (id, description, merchant_id, lat, long) VALUES (5, 'Park Shops', 5, 35.78546665319359, -78.66708463594044);
INSERT INTO locations (id, description, merchant_id, lat, long) VALUES (6, 'Talley', 5, 35.78392567533286, -78.67092696947988);
INSERT INTO locations (id, description, merchant_id, lat, long) VALUES (7, 'Walnut', 6, 35.753166119681715, -78.74569648479638);
INSERT INTO locations (id, description, merchant_id, lat, long) VALUES (8, 'Falls River', 7, 35.906477682429525, -78.59029227485301);

INSERT INTO tags (id, name, occasional, rule) VALUES (1, 'Groceries', 0, 'groc');
INSERT INTO tags (id, name, occasional, rule) VALUES (2, 'Gas', 0, 'gas');
INSERT INTO tags (id, name, occasional, rule) VALUES (3, 'Anarack', 1, null);
INSERT INTO tags (id, name, occasional, rule) VALUES (4, 'University', 0, 'uni');
INSERT INTO tags (id, name, occasional, rule) VALUES (5, 'Dating', 0, 'date');
INSERT INTO tags (id, name, occasional, rule) VALUES (6, 'Third Party Transaction', 0, 'paid for by parents');
INSERT INTO tags (id, name, occasional, rule) VALUES (7, 'Eating Out', 0, 'eatout');
INSERT INTO tags (id, name, occasional, rule) VALUES (8, 'Winter Park Trip', 1, null);
INSERT INTO tags (id, name, occasional, rule) VALUES (9, 'The Maze Trip', 1, null);
INSERT INTO tags (id, name, occasional, rule) VALUES (10, 'Personal', 0, 'personal');
INSERT INTO tags (id, name, occasional, rule) VALUES (11, 'Coffee', 0, 'coffee');

INSERT INTO accounts (id, name, amount_index, description_index, date_index) VALUES (1, 'Checking', 2, 3, 7);
INSERT INTO accounts (id, name, amount_index, description_index, date_index) VALUES (2, 'Savings', 3, 1, 5);

INSERT INTO statements (id, date, file_name, account_id, starting_balance, reconciled) VALUES (1, '2019-02-14 00:00:00', 'BOA.csv', 1, 3235.45, 1);
INSERT INTO statements (id, date, file_name, account_id, starting_balance, reconciled) VALUES (2, '2020-07-08 00:00:00', 'BOA1.csv', 1, 664.45, 1);
INSERT INTO statements (id, date, file_name, account_id, starting_balance, reconciled) VALUES (3, '2023-07-20 00:00:00', 'NEWBOA.csv', 1, 3825.01, 0);
INSERT INTO statements (id, date, file_name, account_id, starting_balance, reconciled) VALUES (4, '2018-12-21 00:00:00', 'DISCOVER.csv', 2, 517.01, 1);
INSERT INTO statements (id, date, file_name, account_id, starting_balance, reconciled) VALUES (5, '2019-08-25 00:00:00', null, 2, 320.93, 1);
INSERT INTO statements (id, date, file_name, account_id, starting_balance, reconciled) VALUES (6, '2021-04-22 00:00:00', 'NEWDISCOVER.csv', 2, 500.33, 0);

INSERT INTO mer_tag_defaults (merchant_id, tag_id) VALUES (1, 5);
INSERT INTO mer_tag_defaults (merchant_id, tag_id) VALUES (1, 7);
INSERT INTO mer_tag_defaults (merchant_id, tag_id) VALUES (2, 7);
INSERT INTO mer_tag_defaults (merchant_id, tag_id) VALUES (4, 10);
INSERT INTO mer_tag_defaults (merchant_id, tag_id) VALUES (5, 11);
INSERT INTO mer_tag_defaults (merchant_id, tag_id) VALUES (6, 1);
INSERT INTO mer_tag_defaults (merchant_id, tag_id) VALUES (8, 10);
INSERT INTO mer_tag_defaults (merchant_id, tag_id) VALUES (9, 10);

INSERT INTO transactions (id, description, merchant_id, reconciled, date, statement_id, receipt_file_name, lat, long, account_id, transfer_trans_id) VALUES (1, 'Date with Sara', 1, 0, '2020-08-27 21:14:40', null, 'IMAGE4.jpeg', 35.868317424041166, -78.62154243252625, 1, null);
INSERT INTO transactions (id, description, merchant_id, reconciled, date, statement_id, receipt_file_name, lat, long, account_id, transfer_trans_id) VALUES (2, 'New Macbook', 4, 1, '2020-10-09 19:01:21', 5, 'IMAGE8932.png', 35.840809717971595, -78.68013948171635, 2, null);
INSERT INTO transactions (id, description, merchant_id, reconciled, date, statement_id, receipt_file_name, lat, long, account_id, transfer_trans_id) VALUES (3, 'DND Dice', 9, 1, '2023-05-04 23:44:29', 1, 'IMAGE22.png', null, null, 1, null);
INSERT INTO transactions (id, description, merchant_id, reconciled, date, statement_id, receipt_file_name, lat, long, account_id, transfer_trans_id) VALUES (4, 'Things from Amazon', 3, 1, '2020-09-28 19:26:10', 1, null, null, null, 1, null);
INSERT INTO transactions (id, description, merchant_id, reconciled, date, statement_id, receipt_file_name, lat, long, account_id, transfer_trans_id) VALUES (5, 'Transfer From Savings', null, 0, '2021-02-15 02:32:18', null, null, null, null, 2, null);
INSERT INTO transactions (id, description, merchant_id, reconciled, date, statement_id, receipt_file_name, lat, long, account_id, transfer_trans_id) VALUES (6, 'Transfer Into Checking', null, 0, '2021-02-15 02:33:05', null, null, null, null, 1, null);
UPDATE transactions SET transfer_trans_id = 6 WHERE id = 5;
UPDATE transactions SET transfer_trans_id = 5 WHERE id = 6;

INSERT INTO amounts (id, amount, transaction_id, description) VALUES (1, 20.54, 1, null);
INSERT INTO amounts (id, amount, transaction_id, description) VALUES (2, 1245.34, 2, null);
INSERT INTO amounts (id, amount, transaction_id, description) VALUES (3, 12.98, 3, null);
INSERT INTO amounts (id, amount, transaction_id, description) VALUES (4, 34.82, 4, 'PC Parts');
INSERT INTO amounts (id, amount, transaction_id, description) VALUES (5, 12.63, 4, 'Textbook');
INSERT INTO amounts (id, amount, transaction_id, description) VALUES (6, -100, 5, null);
INSERT INTO amounts (id, amount, transaction_id, description) VALUES (7, 100, 6, null);

INSERT INTO amount_tags (amount_id, tag_id) VALUES (1, 5);
INSERT INTO amount_tags (amount_id, tag_id) VALUES (1, 7);
INSERT INTO amount_tags (amount_id, tag_id) VALUES (2, 4);
INSERT INTO amount_tags (amount_id, tag_id) VALUES (2, 10);
INSERT INTO amount_tags (amount_id, tag_id) VALUES (3, 10);
INSERT INTO amount_tags (amount_id, tag_id) VALUES (4, 3);
INSERT INTO amount_tags (amount_id, tag_id) VALUES (5, 4);