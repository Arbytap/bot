import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { authApi } from "../../api/auth";
import { useAuthStore } from "../../lib/store";
import { PageHeader } from "../../components/layout/PageHeader";
import { Spinner } from "../../components/ui/Spinner";
import { COMPANY_TYPE_LABELS } from "../../lib/helpers";
import type { Company } from "../../types";

export function SwitchCompanyPage() {
  const navigate = useNavigate();
  const { setUser, setCurrentCompany, user } = useAuthStore();
  const qc = useQueryClient();

  const { data: myCompanies, isLoading } = useQuery({
    queryKey: ["my-companies"],
    queryFn: authApi.myCompanies,
  });

  const switchMutation = useMutation({
    mutationFn: (companyId: string) => authApi.switchCompany(companyId),
    onSuccess: (updatedUser) => {
      setUser(updatedUser);
      const company = myCompanies?.find((r) => r.company.id === updatedUser.current_company_id);
      if (company) setCurrentCompany(company.company);
      qc.invalidateQueries();
      navigate("/projects");
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-24">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div>
      <PageHeader title="Выбор организации" subtitle="От имени какой организации вы работаете?" />
      <div className="p-6 max-w-2xl">
        <div className="space-y-3">
          {myCompanies?.map(({ company, role }) => (
            <button
              key={company.id}
              onClick={() => switchMutation.mutate(company.id)}
              disabled={switchMutation.isPending}
              className={`w-full text-left card p-4 hover:border-blue-400 hover:shadow-md transition-all ${
                user?.current_company_id === company.id
                  ? "border-blue-500 ring-2 ring-blue-200"
                  : ""
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium text-gray-900">{company.short_name}</div>
                  <div className="text-sm text-gray-500">{company.name}</div>
                  {company.inn && (
                    <div className="text-xs text-gray-400 mt-0.5">ИНН: {company.inn}</div>
                  )}
                </div>
                <div className="flex flex-col items-end gap-1">
                  <span className="badge bg-blue-100 text-blue-800">
                    {COMPANY_TYPE_LABELS[company.company_type]}
                  </span>
                  <span className="text-xs text-gray-400">{role}</span>
                  {user?.current_company_id === company.id && (
                    <span className="badge bg-green-100 text-green-700">Текущая</span>
                  )}
                </div>
              </div>
            </button>
          ))}
          {!myCompanies?.length && (
            <div className="text-center py-12 text-gray-400">
              Вы не привязаны ни к одной организации.
              <br />
              Обратитесь к администратору.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
