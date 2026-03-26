import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { sedApi } from "../../api/sed";
import { PageHeader } from "../../components/layout/PageHeader";
import { Badge } from "../../components/ui/Badge";
import { Pagination } from "../../components/ui/Pagination";
import { Spinner } from "../../components/ui/Spinner";
import { EmptyState } from "../../components/ui/EmptyState";
import { CHAIN_DIRECTION_LABELS, formatDate } from "../../lib/helpers";
import type { ChainDirection } from "../../types";

export function ChainsPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [direction, setDirection] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["chains", page, direction],
    queryFn: () => sedApi.listChains({ page, page_size: 20, direction: direction || undefined }),
  });

  return (
    <div>
      <PageHeader
        title="Цепочки переписки"
        subtitle={data ? `Всего: ${data.total}` : undefined}
      />

      <div className="flex gap-3 px-6 py-3 bg-white border-b border-gray-200">
        {[
          { value: "", label: "Все" },
          { value: "incoming", label: "Входящие" },
          { value: "outgoing", label: "Исходящие" },
          { value: "mixed", label: "Смешанные" },
        ].map((opt) => (
          <button
            key={opt.value}
            onClick={() => { setDirection(opt.value); setPage(1); }}
            className={`text-sm px-3 py-1 rounded-full transition-colors ${
              direction === opt.value
                ? "bg-blue-600 text-white"
                : "bg-gray-100 text-gray-600 hover:bg-gray-200"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      <div className="card mx-6 my-4">
        {isLoading ? (
          <div className="flex justify-center py-12"><Spinner /></div>
        ) : !data?.items.length ? (
          <EmptyState title="Нет цепочек переписки" />
        ) : (
          <>
            <table className="w-full">
              <thead>
                <tr className="text-left text-xs text-gray-500 uppercase border-b border-gray-100">
                  <th className="px-4 py-3">Тема</th>
                  <th className="px-4 py-3">Направление</th>
                  <th className="px-4 py-3 text-center">Писем</th>
                  <th className="px-4 py-3">Создана</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {data.items.map((chain) => (
                  <tr key={chain.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-gray-900 font-medium">{chain.subject}</td>
                    <td className="px-4 py-3">
                      <Badge
                        label={CHAIN_DIRECTION_LABELS[chain.direction as ChainDirection]}
                        className="bg-gray-100 text-gray-700"
                      />
                    </td>
                    <td className="px-4 py-3 text-center text-gray-500">{chain.letters_count}</td>
                    <td className="px-4 py-3 text-gray-400">{formatDate(chain.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            <Pagination page={data.page} pages={data.pages} total={data.total} onPageChange={setPage} />
          </>
        )}
      </div>
    </div>
  );
}
