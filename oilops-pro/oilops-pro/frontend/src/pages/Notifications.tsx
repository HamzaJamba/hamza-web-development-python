import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { CheckCheck } from "lucide-react";
import { Link } from "react-router-dom";

import { Badge, Button, Card, Empty, PageHeader, Spinner } from "../components/ui";
import { api, Row } from "../lib/api";
import { ago, pretty } from "../lib/format";

export default function Notifications() {
  const qc = useQueryClient();
  const q = useQuery({ queryKey: ["notifs"], queryFn: async () => (await api.get("/notifications/", { params: { page_size: 100 } })).data.results as Row[] });
  const done = () => { qc.invalidateQueries({ queryKey: ["notifs"] }); qc.invalidateQueries({ queryKey: ["unread"] }); qc.invalidateQueries({ queryKey: ["notif-recent"] }); };
  const readAll = useMutation({ mutationFn: () => api.post("/notifications/read-all/"), onSuccess: done });
  const read = useMutation({ mutationFn: (id: number) => api.post(`/notifications/${id}/read/`), onSuccess: done });
  return (
    <div>
      <PageHeader title="Notifications" subtitle="Maintenance due, low stock, incidents, sensor alerts and work order updates." actions={<Button onClick={() => readAll.mutate()} loading={readAll.isPending}><CheckCheck className="h-4 w-4" />Mark all as read</Button>} />
      <Card pad={false}>
        {q.isLoading && <Spinner />}
        {q.data?.length === 0 && <Empty title="No notifications yet" hint="Alerts and updates relevant to your role will appear here." />}
        <ul className="divide-y divide-line">
          {q.data?.map((n) => (
            <li key={n.id} className={`flex items-start justify-between gap-4 px-4 py-3 ${n.is_read ? "" : "bg-sky-50/60"}`}>
              <div className="min-w-0">
                <Link to={n.link || "#"} onClick={() => !n.is_read && read.mutate(n.id)} className={`block ${n.is_read ? "" : "font-semibold"} text-ink-900 hover:underline`}>{n.title}</Link>
                {n.message && <p className="mt-0.5 text-sm text-slate-600">{n.message}</p>}
                <p className="mt-1 text-xs text-slate-500">{pretty(n.kind)} · {ago(n.created_at)}</p>
              </div>
              <div className="flex shrink-0 items-center gap-2">{n.severity !== "info" && <Badge value={n.severity.toUpperCase()} />}{!n.is_read && <Button variant="ghost" onClick={() => read.mutate(n.id)}>Mark read</Button>}</div>
            </li>
          ))}
        </ul>
      </Card>
    </div>
  );
}
