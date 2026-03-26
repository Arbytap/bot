import { useParams, useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { sedApi } from "../../api/sed";
import { PageHeader } from "../../components/layout/PageHeader";
import { Badge } from "../../components/ui/Badge";
import { Spinner } from "../../components/ui/Spinner";
import {
  LETTER_TYPE_LABELS, LETTER_STATUS_LABELS, LETTER_STATUS_COLORS,
  formatDate, formatDateTime, formatFileSize,
} from "../../lib/helpers";
import type { LetterType, LetterStatus } from "../../types";

export function LetterDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const { data: thread, isLoading } = useQuery({
    queryKey: ["letter-thread", id],
    queryFn: () => sedApi.getThread(id!),
    enabled: !!id,
  });

  if (isLoading) {
    return <div className="flex justify-center py-24"><Spinner size="lg" /></div>;
  }
  if (!thread?.letter) return <div className="p-8 text-gray-500">Письмо не найдено</div>;

  const { letter, reply_to, replies, chain_letters } = thread;

  return (
    <div>
      <PageHeader
        title={letter.subject || `Письмо ${letter.number || letter.id.slice(0, 8)}`}
        subtitle={`${LETTER_TYPE_LABELS[letter.letter_type as LetterType]} · ${formatDate(letter.letter_date)}`}
        actions={
          <div className="flex items-center gap-2">
            <Badge
              label={LETTER_STATUS_LABELS[letter.status as LetterStatus]}
              className={LETTER_STATUS_COLORS[letter.status as LetterStatus]}
            />
            <button className="btn-secondary" onClick={() => navigate(-1)}>
              ← Назад
            </button>
          </div>
        }
      />

      <div className="flex gap-6 p-6">
        {/* Main card */}
        <div className="flex-1 space-y-4">
          <div className="card p-5">
            <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-4">
              Реквизиты
            </h2>
            <div className="grid grid-cols-2 gap-3">
              <Field label="Наш номер" value={letter.number || "—"} />
              <Field label="Номер контрагента" value={letter.org_number || "—"} />
              <Field label="Дата письма" value={formatDate(letter.letter_date)} />
              <Field label="Тип" value={LETTER_TYPE_LABELS[letter.letter_type as LetterType]} />
              <Field label="От кого" value={letter.from_company?.short_name || "—"} />
              <Field label="Кому" value={letter.to_company?.short_name || "—"} />
              <Field label="Владелец" value={letter.owner_company.short_name} />
              <Field label="Зарегистрировано" value={formatDateTime(letter.created_at)} />
            </div>
            {letter.resolution && (
              <div className="mt-4 p-3 bg-yellow-50 rounded-md border border-yellow-200">
                <div className="text-xs text-yellow-600 font-medium mb-1">Резолюция</div>
                <div className="text-sm text-gray-800">{letter.resolution}</div>
              </div>
            )}
            {letter.note && (
              <div className="mt-3 p-3 bg-gray-50 rounded-md">
                <div className="text-xs text-gray-400 font-medium mb-1">Примечание</div>
                <div className="text-sm text-gray-700">{letter.note}</div>
              </div>
            )}
          </div>

          {/* Files */}
          {letter.files.length > 0 && (
            <div className="card p-5">
              <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-3">
                Вложения ({letter.files.length})
              </h2>
              <div className="space-y-2">
                {letter.files.map((f) => (
                  <a
                    key={f.id}
                    href={sedApi.downloadFileUrl(letter.id, f.id)}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center justify-between p-2 rounded-md hover:bg-gray-50 group"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-lg">📎</span>
                      <div>
                        <div className="text-sm text-blue-600 group-hover:underline">{f.original_name}</div>
                        <div className="text-xs text-gray-400">{formatFileSize(f.size)}</div>
                      </div>
                    </div>
                    <span className="text-xs text-gray-300">{formatDate(f.uploaded_at)}</span>
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Thread sidebar */}
        <div className="w-72 space-y-4">
          {reply_to && (
            <div className="card p-4">
              <div className="text-xs text-gray-400 uppercase font-medium mb-2">Ответ на:</div>
              <div
                className="cursor-pointer hover:text-blue-600"
                onClick={() => navigate(`/letters/${reply_to.id}`)}
              >
                <div className="text-sm font-medium">{reply_to.number || reply_to.org_number || "—"}</div>
                <div className="text-xs text-gray-500">{formatDate(reply_to.letter_date)}</div>
              </div>
            </div>
          )}

          {replies.length > 0 && (
            <div className="card p-4">
              <div className="text-xs text-gray-400 uppercase font-medium mb-2">
                Ответы ({replies.length})
              </div>
              <div className="space-y-2">
                {replies.map((r) => (
                  <div
                    key={r.id}
                    className="cursor-pointer hover:text-blue-600 text-sm border-l-2 border-blue-200 pl-2"
                    onClick={() => navigate(`/letters/${r.id}`)}
                  >
                    {r.number || r.org_number || "—"} · {formatDate(r.letter_date)}
                  </div>
                ))}
              </div>
            </div>
          )}

          {chain_letters.length > 0 && (
            <div className="card p-4">
              <div className="text-xs text-gray-400 uppercase font-medium mb-2">
                Цепочка ({chain_letters.length})
              </div>
              <div className="space-y-1.5">
                {chain_letters.map((l) => (
                  <div
                    key={l.id}
                    className="cursor-pointer text-sm text-gray-600 hover:text-blue-600 flex items-center gap-1.5"
                    onClick={() => navigate(`/letters/${l.id}`)}
                  >
                    <span className="text-xs">
                      {l.letter_type === "incoming" ? "📥" : "📤"}
                    </span>
                    <span className="truncate">
                      {l.number || l.org_number || l.id.slice(0, 8)}
                    </span>
                    <span className="text-gray-300 text-xs shrink-0">{formatDate(l.letter_date)}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-gray-400">{label}</div>
      <div className="text-sm text-gray-900 font-medium mt-0.5">{value}</div>
    </div>
  );
}
