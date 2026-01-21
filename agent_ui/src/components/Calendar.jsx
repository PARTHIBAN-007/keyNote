import React, { useState } from "react";

const daysInMonth = (month, year) => new Date(year, month + 1, 0).getDate();
const getFirstDayOfWeek = (month, year) => new Date(year, month, 1).getDay();

// Check if an event spans across a given date
const eventSpansDate = (event, dateStr) => {
  const eventStart = new Date(event.start_time);
  const eventEnd = new Date(event.end_time);
  const checkDate = new Date(dateStr + "T00:00:00");
  
  return checkDate >= eventStart && checkDate <= eventEnd;
};

const Calendar = ({ events, onDateClick }) => {
  const today = new Date();
  const [currentMonth, setCurrentMonth] = useState(today.getMonth());
  const [currentYear, setCurrentYear] = useState(today.getFullYear());

  const days = daysInMonth(currentMonth, currentYear);
  const firstDay = getFirstDayOfWeek(currentMonth, currentYear);
  const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

  const prevMonth = () => {
    if (currentMonth === 0) {
      setCurrentMonth(11);
      setCurrentYear(currentYear - 1);
    } else {
      setCurrentMonth(currentMonth - 1);
    }
  };
  
  const nextMonth = () => {
    if (currentMonth === 11) {
      setCurrentMonth(0);
      setCurrentYear(currentYear + 1);
    } else {
      setCurrentMonth(currentMonth + 1);
    }
  };

  const renderDays = () => {
    const cells = [];
    for (let i = 0; i < firstDay; i++) {
      cells.push(<div key={`empty-${i}`} className="bg-slate-100 rounded p-2 aspect-square" />);
    }
    for (let day = 1; day <= days; day++) {
      const dateStr = `${currentYear}-${String(currentMonth + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
      const hasEvent = events.some(event => eventSpansDate(event, dateStr));
      const isToday = day === today.getDate() && currentMonth === today.getMonth() && currentYear === today.getFullYear();
      
      cells.push(
        <button
          key={dateStr}
          className={`rounded font-semibold text-sm transition-all aspect-square flex items-center justify-center ${
            hasEvent 
              ? "bg-emerald-500 text-white shadow hover:bg-emerald-600 hover:shadow-md" 
              : isToday 
              ? "bg-indigo-500 text-white shadow border-2 border-indigo-300 hover:bg-indigo-600" 
              : "bg-slate-100 text-slate-700 hover:bg-slate-200 border border-slate-200"
          }`}
          onClick={() => onDateClick(dateStr)}
        >
          {day}
        </button>
      );
    }
    return cells;
  };

  return (
    <div className="bg-white rounded-lg shadow border border-slate-200 p-4 h-full flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <button 
          onClick={prevMonth} 
          className="px-3 py-2 rounded border border-indigo-300 hover:bg-indigo-50 text-indigo-600 font-semibold transition text-lg"
        >
          ←
        </button>
        <div className="font-bold text-lg text-slate-800 text-center flex-1">
          {monthNames[currentMonth]} {currentYear}
        </div>
        <button 
          onClick={nextMonth}
          className="px-3 py-2 rounded border border-indigo-300 hover:bg-indigo-50 text-indigo-600 font-semibold transition text-lg"
        >
          →
        </button>
      </div>
      
      <div className="grid grid-cols-7 gap-1 flex-1">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
          <div key={d} className="text-center text-xs font-bold text-slate-600 py-1">
            {d}
          </div>
        ))}
        {renderDays()}
      </div>
      
      <div className="mt-4 pt-3 border-t border-slate-200 space-y-2">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-emerald-500"></div>
          <span className="text-xs text-slate-600">Event scheduled</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded bg-indigo-500"></div>
          <span className="text-xs text-slate-600">Today</span>
        </div>
      </div>
    </div>
  );
};

export default Calendar;
