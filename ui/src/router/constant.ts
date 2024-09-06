import OverviewSubView from '../views/subviews/overview/index.vue'
import RealTimeQuerySubView from '../views/subviews/rtq/index.vue'
import ExportRecordSubView from '../views/subviews/export-record/index.vue'
import QueryScenarioSubView from '../views/subviews/query-scenario/index.vue'
import StandingBookSubView from '../views/subviews/standing-book/index.vue'
import UserManagementSubView from '../views/subviews/user-management/index.vue'
import RoleManagementSubView from '../views/subviews/role-management/index.vue'
import PermManagementSubView from '../views/subviews/perm-management/index.vue'
import FieldManagementSubView from '../views/subviews/field-management/index.vue'
import FieldCollectSubView from '../views/subviews/field-collect/index.vue'
import ModelManagementSubView from '../views/subviews/model-management/index.vue'
import GraphManagementSubView from '../views/subviews/graph-management/index.vue'
import AdapterManagementSubView from '../views/subviews/adapter-management/index.vue'
import MappingManagementSubView from '../views/subviews/mapping-management/index.vue'
import PlanManagementSubView from '../views/subviews/plan-management/index.vue'
import TaskManagementSubView from '../views/subviews/task-management/index.vue'
import LicenseSubView from '../views/subviews/license/index.vue'
import AboutSubView from '../views/subviews/about/index.vue'

export const ROUTES_MAP = new Map([
    ['overview', {
        path: '/overview',
        name: 'overview',
        component: OverviewSubView,
    }],
    ['real_time_query', {
        path: '/rtq',
        name: 'real_time_query',
        component: RealTimeQuerySubView,
    }],
    ['export_record', {
        path: '/export',
        name: 'export_record',
        component: ExportRecordSubView,
    }],
    ['query_scenario', {
        path: '/qscenario',
        name: 'query_scenario',
        component: QueryScenarioSubView,
    }],
    ['standing_book', {
        path: '/sbook',
        name: 'standing_book',
        component: StandingBookSubView,
    }],
    ['user_management', {
        path: '/users',
        name: 'user_management',
        component: UserManagementSubView,
    }],
    ['role_management', {
        path: '/roles',
        name: 'role_management',
        component: RoleManagementSubView,
    }],
    ['perm_management', {
        path: '/perms',
        name: 'perm_management',
        component: PermManagementSubView,
    }],
    ['field_management', {
        path: '/fields',
        name: 'field_management',
        component: FieldManagementSubView,
    }],
    ['field_collect', {
        path: '/fcollect',
        name: 'field_collect',
        component: FieldCollectSubView,
    }],
    ['model_management', {
        path: '/models',
        name: 'model_management',
        component: ModelManagementSubView,
    }],
    ['graph_management', {
        path: '/graphs',
        name: 'graph_management',
        component: GraphManagementSubView,
    }],
    ['adapter_management', {
        path: '/adapters',
        name: 'adapter_management',
        component: AdapterManagementSubView,
    }],
    ['mapping_management', {
        path: '/mappings',
        name: 'mapping_management',
        component: MappingManagementSubView,
    }],
    ['plan_management', {
        path: '/plans',
        name: 'plan_management',
        component: PlanManagementSubView,
    }],
    ['task_management', {
        path: '/tasks',
        name: 'task_management',
        component: TaskManagementSubView,
    }],
    ['license', {
        path: '/license',
        name: 'license',
        component: LicenseSubView,
    }],
    ['about', {
        path: '/about',
        name: 'about',
        component: AboutSubView,
    }]
])