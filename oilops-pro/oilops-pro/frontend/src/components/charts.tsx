import { ArcElement, BarElement, CategoryScale, Chart as ChartJS, Filler, Legend, LinearScale, LineElement, PointElement, Tooltip } from "chart.js";
import { Bar, Doughnut, Line } from "react-chartjs-2";

ChartJS.register(ArcElement, BarElement, CategoryScale, LinearScale, LineElement, PointElement, Tooltip, Legend, Filler);
ChartJS.defaults.font.family = "Barlow, sans-serif";
ChartJS.defaults.color = "#4a5f63";

export const PALETTE = ["#1f7a8c", "#e4572e", "#c98a12", "#2f855a", "#6b4ea0", "#2c6068"];
const grid = { color: "#e6ebec" };
type S = { label: string; data: number[]; color?: string };

export function StackedBars({ labels, series, height = 240 }: { labels: string[]; series: S[]; height?: number }) {
  return (
    <div style={{ height }}>
      <Bar
        data={{ labels, datasets: series.map((s, i) => ({ label: s.label, data: s.data, backgroundColor: s.color ?? PALETTE[i % PALETTE.length], borderRadius: 2 })) }}
        options={{ responsive: true, maintainAspectRatio: false, scales: { x: { stacked: true, grid: { display: false } }, y: { stacked: true, grid } }, plugins: { legend: { position: "bottom", labels: { boxWidth: 10 } } } }}
      />
    </div>
  );
}

export function Lines({ labels, series, height = 240, fill }: { labels: string[]; series: S[]; height?: number; fill?: boolean }) {
  return (
    <div style={{ height }}>
      <Line
        data={{ labels, datasets: series.map((s, i) => ({ label: s.label, data: s.data, borderColor: s.color ?? PALETTE[i % PALETTE.length], backgroundColor: (s.color ?? PALETTE[i % PALETTE.length]) + "22", fill, tension: 0.3, pointRadius: 2, borderWidth: 2 })) }}
        options={{ responsive: true, maintainAspectRatio: false, scales: { x: { grid: { display: false }, ticks: { maxTicksLimit: 8 } }, y: { grid } }, plugins: { legend: { display: series.length > 1, position: "bottom", labels: { boxWidth: 10 } } } }}
      />
    </div>
  );
}

export function Donut({ labels, data, colors, height = 220 }: { labels: string[]; data: number[]; colors?: string[]; height?: number }) {
  return (
    <div style={{ height }}>
      <Doughnut data={{ labels, datasets: [{ data, backgroundColor: colors ?? PALETTE, borderWidth: 2, borderColor: "#fff" }] }}
        options={{ responsive: true, maintainAspectRatio: false, cutout: "62%", plugins: { legend: { position: "right", labels: { boxWidth: 10 } } } }} />
    </div>
  );
}

export function HBars({ labels, data, color = "#1f7a8c", height = 240 }: { labels: string[]; data: number[]; color?: string; height?: number }) {
  return (
    <div style={{ height }}>
      <Bar data={{ labels, datasets: [{ data, backgroundColor: color, borderRadius: 2 }] }}
        options={{ indexAxis: "y", responsive: true, maintainAspectRatio: false, scales: { x: { grid }, y: { grid: { display: false } } }, plugins: { legend: { display: false } } }} />
    </div>
  );
}
