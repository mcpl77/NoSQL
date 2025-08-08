
/var/run/tarantool/sys_env/default/instance-001/tarantool.control> box.func.cheap_flights:call({3000})
---
- - [1, 'Aeroflot', '01.01.2025', 'Moscow', 'London', 2500]
  - [3, 'Aeroflot', '02.01.2025', 'Moscow', 'Paris', 2800]
  - [4, 'Pobeda', '01.01.2025', 'St. Petersburg', 'Moscow', 2900]
  - [5, 'Ural Airlines', '01.01.2025', 'Ekaterinburg', 'Sochi', 2700]
...

/var/run/tarantool/sys_env/default/instance-001/tarantool.control> -- Проверим все записи
box.space.tickets:select()
---
- - [1, 'Aeroflot', '01.01.2025', 'Moscow', 'London', 2500]
  - [2, 'S7', '01.01.2025', 'Novosibirsk', 'Moscow', 3500]
  - [3, 'Aeroflot', '02.01.2025', 'Moscow', 'Paris', 2800]
  - [4, 'Pobeda', '01.01.2025', 'St. Petersburg', 'Moscow', 2900]
  - [5, 'Ural Airlines', '01.01.2025', 'Ekaterinburg', 'Sochi', 2700]
...

/var/run/tarantool/sys_env/default/instance-001/tarantool.control> return cheap_flights(3000)
---
- - [1, 'Aeroflot', '01.01.2025', 'Moscow', 'London', 2500]
  - [3, 'Aeroflot', '02.01.2025', 'Moscow', 'Paris', 2800]
  - [4, 'Pobeda', '01.01.2025', 'St. Petersburg', 'Moscow', 2900]
  - [5, 'Ural Airlines', '01.01.2025', 'Ekaterinburg', 'Sochi', 2700]
...


/var/run/tarantool/sys_env/default/instance-001/tarantool.control> cheap_flights_print(3000)
---
- 4
...

/var/run/tarantool/sys_env/default/instance-001/tarantool.control> box.func.cheap_flights:call({3000})
---
- - [1, 'Aeroflot', '01.01.2025', 'Moscow', 'London', 2500]
  - [3, 'Aeroflot', '02.01.2025', 'Moscow', 'Paris', 2800]
  - [4, 'Pobeda', '01.01.2025', 'St. Petersburg', 'Moscow', 2900]
  - [5, 'Ural Airlines', '01.01.2025', 'Ekaterinburg', 'Sochi', 2700]
...

/var/run/tarantool/sys_env/default/instance-001/tarantool.control> cheap_flights(3000)
---
- - [1, 'Aeroflot', '01.01.2025', 'Moscow', 'London', 2500]
  - [3, 'Aeroflot', '02.01.2025', 'Moscow', 'Paris', 2800]
  - [4, 'Pobeda', '01.01.2025', 'St. Petersburg', 'Moscow', 2900]
  - [5, 'Ural Airlines', '01.01.2025', 'Ekaterinburg', 'Sochi', 2700]
...
