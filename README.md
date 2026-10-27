# Battery Solar Optimizer for Home Assistant

[🇺🇦 Українська](#українська) | [🇬🇧 English](#english)

---

<a name="українська"></a>
## 🇺🇦 Battery Solar Optimizer

**Battery Solar Optimizer** — це розумний кастомний компонент для Home Assistant, створений для автоматичного розрахунку оптимального рівня зарядки акумулятора вночі (за дешевим тарифом) з урахуванням прогнозу сонячної генерації (Solcast) та вашого реального енергоспоживання.

### 🎯 Навіщо потрібен цей плагін?
Якщо ви маєте гібридний інвертор, домашню батарею та сонячні панелі, перед вами часто постає питання: *«До якого рівня зарядити батарею вночі, щоб і повністю використати завтрашнє сонце, і не залишитися без світла вранці?»*

Цей інтегрований алгоритм автоматично адаптується під ваші звички та погоду:
- **Адаптивне споживання з персистентністю:** Аналізує погодинне енергоспоживання будинку (окремо для буднів та вихідних) за допомогою алгоритму згладжування (EMA). Історія споживання накопичується з часом.
- **Швидкий старт (Ручне заповнення):** Щоб не чекати кілька днів на збір реальної статистики, ви можете вручну вписати свої типові показники споживання по годинах у файл сховища `.storage/battery_optimizer_history`.
- **Інтеграція з Solcast:** Автоматично визначає години сонячної активності на основі детального прогнозу Solcast (з урахуванням порогу генерації від 200 Вт).
- **Гнучкі режими роботи:**
  * *Max 100% Charge (Зима):* Розраховує необхідний нічний дозаряд з урахуванням покриття денних потреб будинку сонячною генерацією та заданою похибкою.
  * *Max Solar Utilization (Літо):* Зберігає резерв лише на ранок і мінімальний SoC, щоб дати сонячним панелям максимально зарядити батарею.

### ⚙️ Параметри налаштування
Для коректної роботи потрібно налаштувати наступні параметри:

| Параметр | Назва в інтерфейсі | Опис |
| :--- | :--- | :--- |
| `consumption_sensor` | Home Energy Consumption Sensor (kWh) | Ваш лічильник накопичувальної енергії будинку в кВт·год. |
| `solcast_today_sensor` | Solcast Forecast Sensor (TODAY) | Сенсор Solcast із прогнозом генерації енергії на **сьогодні**. |
| `solcast_tomorrow_sensor` | Solcast Forecast Sensor (TOMORROW) | Сенсор Solcast із прогнозом генерації енергії на **завтра**. |
| `battery_soc_sensor` | Battery SoC Sensor (%) | Сенсор поточного рівня заряду вашого акумулятора (у %). |
| `battery_capacity_kwh` | Battery Capacity (kWh) | Повна ємність вашого акумулятора в кВт·год. |
| `min_soc` | Minimum State of Charge (%) | Мінімальний допустимий рівень розряду батареї (у відсотках). |
| `soc_offset` | Night Charge Offset (%) | Бажана похибка/зміщення нічного заряду (наприклад, `+10%` до розрахунку). |
| `history_days` | History Depth for Analysis (Days) | Кількість днів для аналізу звичок споживання (впливає на згладжування EMA). |
| `night_start` | Night Tariff Start Time | Час початку нічного тарифу (наприклад, `23:00`). |
| `night_end` | Night Tariff End Time | Час закінчення нічного тарифу (наприклад, `05:00`). |
| `operation_mode` | Operation Mode | Режим роботи: `Max 100% Charge (Winter)` або `Max Solar Utilization (Summer)`. |

### 📊 Створені сенсори (Observability)
Інтеграція створює повний набір сенсорів для моніторингу та побудови автоматизацій:
- `sensor.target_battery_soc_night` — цільовий відсоток заряду на ніч (%).
- `sensor.target_battery_energy_night` — необхідна ємність на ніч (kWh).
- `sensor.morning_consumption_forecast` — прогнозоване споживання будинку в ранковий період (kWh) (від закінчення нічного тарифу до початку генерації).
- `sensor.day_consumption_forecast` — прогнозоване споживання будинку в години сонячного дня (kWh) (від початку генерації і до кінця генерації).
- `sensor.battery_soc_at_solar_end` — фактичний рівень заряду батареї в момент закінчення сонячної генерації (%).
- `sensor.forecasted_energy_surplus` — прогнозований надлишок енергії (kWh).
- `sensor.realtime_energy_surplus` — поточний реальний надлишок потужності (kW).
- `sensor.night_tariff_start_time` / `sensor.night_tariff_end_time` — час нічного тарифу.
- `sensor.solar_generation_start` / `sensor.solar_generation_end` — розрахований час початку та закінчення сонячної генерації.

### 💡 Порада: Як заповнити історію споживання вручну
За замовчуванням інтеграція використовує дефолтне значення `0.5 кВт·год` на кожну годину, доки не накопичить реальну статистику. Якщо ви хочете закласти свої власні цифри одразу:
1. Перейдіть до папки `.storage` у вашому Home Assistant і відкрийте файл **`battery_optimizer_history`**.
2. У масивах `"workday"` (будні) та `"weekend"` (вихідні) перелічено **24 значення** (від години `0` до години `23`).
3. Ви можете замінити ці `0.5` на свої реальні середні витрати енергії для кожної години доби (у кВт·год).
4. Збережіть файл і зробіть релоад інтеграції — розрахунок одразу базуватиметься на ваших даних!

- Повна підтримка локалізації (українська та англійська мови).
- Сумісність з HACS.

---

<a name="english"></a>
## 🇬🇧 Battery Solar Optimizer

**Battery Solar Optimizer** is a smart custom component for Home Assistant designed to automatically calculate the optimal nighttime battery charge level (during cheap tariff hours) based on Solcast solar generation forecasts and your actual home energy consumption.

### 🎯 Why do you need this plugin?
If you own a hybrid inverter, home battery storage, and solar panels, you often face the question: *“What charge level should I set for the battery at night to fully utilize tomorrow's solar energy while ensuring I don't run out of power in the morning?”*

This built-in algorithm automatically adapts to your habits and the weather:
- **Persistent Adaptive Consumption:** Analyzes hourly home energy consumption (separately for workdays and weekends) using an Exponential Moving Average (EMA) smoothing algorithm. Consumption history builds up over time.
- **Quick Start (Manual Override):** To avoid waiting several days for real statistics to accumulate, you can manually inject your typical hourly consumption values directly into the `.storage/battery_optimizer_history` file.
- **Solcast Integration:** Automatically determines solar production windows from Solcast detailed forecasts (using a 200W generation threshold).
- **Flexible Operating Modes:**
  * *Max 100% Charge (Winter):* Calculates required night charging while accounting for daytime solar offset of home consumption and custom safety offsets.
  * *Max Solar Utilization (Summer):* Keeps only morning headroom plus minimum SoC to maximize solar self-consumption.

### ⚙️ Configuration Parameters
The following parameters must be configured for correct operation:

| Parameter | UI Label | Description |
| :--- | :--- | :--- |
| `consumption_sensor` | Home Energy Consumption Sensor (kWh) | Your cumulative home energy consumption sensor in kWh. |
| `solcast_today_sensor` | Solcast Forecast Sensor (TODAY) | Solcast forecast sensor for **today**. |
| `solcast_tomorrow_sensor` | Solcast Forecast Sensor (TOMORROW) | Solcast forecast sensor for **tomorrow**. |
| `battery_soc_sensor` | Battery SoC Sensor (%) | Sensor tracking your current battery state of charge (%). |
| `battery_capacity_kwh` | Battery Capacity (kWh) | Total capacity of your battery storage in kWh. |
| `min_soc` | Minimum State of Charge (%) | Minimum target state of charge percentage allowed for the battery. |
| `soc_offset` | Night Charge Offset (%) | Desired offset added to the night charge calculation (e.g., `+10%`). |
| `history_days` | History Depth for Analysis (Days) | Number of days used to analyze consumption habits (drives EMA smoothing). |
| `night_start` | Night Tariff Start Time | Start time of your cheap night electricity tariff (e.g., `23:00`). |
| `night_end` | Night Tariff End Time | End time of your cheap night electricity tariff (e.g., `05:00`). |
| `operation_mode` | Operation Mode | Operating strategy: `Max 100% Charge (Winter)` or `Max Solar Utilization (Summer)`. |

### 📊 Exposed Sensors (Observability)
The integration creates a comprehensive set of sensors for monitoring and automations:
- `sensor.target_battery_soc_night` — target battery charge percentage for the night (%).
- `sensor.target_battery_energy_night` — required energy capacity for the night (kWh).
- `sensor.morning_consumption_forecast` — forecasted home consumption during the morning period (kWh) (from night tariff end to generation start).
- `sensor.day_consumption_forecast` — forecasted home consumption during solar hours (kWh) (from generation start to generation end).
- `sensor.battery_soc_at_solar_end` — actual battery SoC captured at the end of solar generation (%).
- `sensor.forecasted_energy_surplus` — forecasted energy surplus (kWh).
- `sensor.realtime_energy_surplus` — real-time power surplus (kW).
- `sensor.night_tariff_start_time` / `sensor.night_tariff_end_time` — night tariff schedule.
- `sensor.solar_generation_start` / `sensor.solar_generation_end` — calculated solar generation start and end times.

### 💡 Tip: How to Manually Populate Consumption History
By default, the integration uses a default value of `0.5 kWh` for each hour until real statistics are collected. If you want to use your own figures right away:
1. Navigate to the `.storage` directory in your Home Assistant and open the **`battery_optimizer_history`** file.
2. The `"workday"` and `"weekend"` arrays list **24 values** (from hour `0` to hour `23`).
3. You can replace these `0.5` entries with your actual average energy expenditure for each hour of the day (in kWh).
4. Save the file and reload the integration — calculations will immediately be based on your data!

- Full localization support (English and Ukrainian).
- HACS compatible.
