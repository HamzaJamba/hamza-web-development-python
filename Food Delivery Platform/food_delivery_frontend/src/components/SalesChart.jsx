import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
} from "chart.js";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

export default function SalesChart({ series }) {
  if (!series || series.length === 0) {
    return (
      <div className="empty-state" style={{ padding: 30 }}>
        <i className="ti ti-chart-line" />
        No sales data yet for this period.
      </div>
    );
  }

  const labels = series.map((row) =>
    new Date(row.day || row.bucket).toLocaleDateString("en-GB", { day: "2-digit", month: "short" })
  );
  const revenue = series.map((row) => Number(row.revenue));

  const data = {
    labels,
    datasets: [
      {
        label: "Revenue (Rs)",
        data: revenue,
        borderColor: "#E8A93B",
        backgroundColor: "rgba(232, 169, 59, 0.15)",
        fill: true,
        tension: 0.35,
        pointRadius: 2,
        pointBackgroundColor: "#E8A93B",
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: "#1F4436",
        titleColor: "#F5EDE0",
        bodyColor: "#F5EDE0",
        borderColor: "#E8A93B55",
        borderWidth: 1,
      },
    },
    scales: {
      x: {
        ticks: { color: "#8FA396", font: { size: 10 } },
        grid: { color: "rgba(255,255,255,0.05)" },
      },
      y: {
        ticks: { color: "#8FA396", font: { size: 10 } },
        grid: { color: "rgba(255,255,255,0.05)" },
        beginAtZero: true,
      },
    },
  };

  return (
    <div style={{ height: 220 }}>
      <Line data={data} options={options} />
    </div>
  );
}
