import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment } from '@react-three/drei';
import styles from './AdminDashboard.module.css'; // 确保样式文件路径正确
import Sidebar from './components/Sidebar.tsx';
import StatisticCard from './components/StatisticCard.tsx';
import ThreeDChart from './components/ThreeDChart.tsx';
import CustomerTable from './components/CustomerTable.tsx';
import ThreeDIcon from './components/ThreeDIcon.tsx';
import Chatbot from './components/Chatbot.tsx';
import RegionModel from './components/RegionModel.tsx';
import ZoomableContainer from './components/ZoomableContainer.tsx';
import { getStatisticData, getRegionData } from '../../services/adminService.ts';
import { StatisticData, ChartData, RegionData } from '../../types/admin.ts';
import { notification } from 'antd';

const AdminDashboard: React.FC = () => {
  const { t, i18n } = useTranslation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [statisticData, setStatisticData] = useState<StatisticData | null>(null);
  const [regionData, setRegionData] = useState<RegionData[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);
  const [zoomElement, setZoomElement] = useState<{
    content: React.ReactNode;
    title: string;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [notificationApi, notificationContext] = notification.useNotification();

  // 图表数据
  const [charts, setCharts] = useState<ChartData[]>([]);

  useEffect(() => {
    console.log('AdminDashboard mounted');
  }, []);

  useEffect(() => {
    // 加载统计数据
    const loadData = async () => {
      try {
        setLoading(true);
        const [statsRes, regionsRes] = await Promise.all([
          getStatisticData(selectedRegion || undefined),
          getRegionData()
        ]);
        
        setStatisticData(statsRes.data);
        setRegionData(regionsRes.data);
        
        // 初始化图表数据
        initCharts(statsRes.data);
        
        if (selectedRegion) {
          const regionName = regionData.find(r => r.id === selectedRegion)?.name[i18n.language] || '';
          notificationApi.success({
            message: t('notification.regionSelected'),
            description: t('notification.regionDataLoaded', { region: regionName }),
          });
        }
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
        notificationApi.error({
          message: t('notification.loadFailed'),
          description: t('notification.dataLoadError'),
        });
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [selectedRegion, i18n.language, notificationApi, regionData]);

  // 初始化图表数据
  const initCharts = (stats: StatisticData) => {
    // 申请状态分布饼图
    const statusPie: ChartData = {
      type: 'pie',
      title: {
        zh: '申请状态分布',
        en: 'Application Status Distribution',
        ja: '申請状況分布'
      },
      data: [
        { name: t('status.pending'), value: stats.pendingApplications, color: '#3498db' },
        { name: t('status.approved'), value: stats.approvedApplications, color: '#2ecc71' },
        { name: t('status.rejected'), value: stats.rejectedApplications, color: '#e74c3c' }
      ],
      dimensions: { x: 10, y: 10, z: 5 }
    };

    // 月度销售柱状图
    const monthlyBar: ChartData = {
      type: 'bar',
      title: {
        zh: '月度销售额',
        en: 'Monthly Sales',
        ja: '月間売上高'
      },
      data: stats.monthlySales.map((item, index) => ({
        name: item.month,
        value: item.amount,
        color: `hsl(${index * 30}, 70%, 60%)`
      })),
      dimensions: { x: 15, y: 8, z: 0.5 }
    };

    // 区域销售折线图
    const regionLine: ChartData = {
      type: 'line',
      title: {
        zh: '区域销售趋势',
        en: 'Regional Sales Trend',
        ja: '地域販売動向'
      },
      data: stats.regionalSales.map((item, index) => ({
        name: item.region,
        value: item.amount,
        color: `hsl(${index * 45}, 70%, 50%)`
      })),
      dimensions: { x: 15, y: 8, z: 0.3 }
    };

    setCharts([statusPie, monthlyBar, regionLine]);
  };

  // 处理区域选择
  const handleRegionSelect = (regionId: string) => {
    setSelectedRegion(regionId);
  };

  // 处理图表放大
  const handleChartZoom = (chart: React.ReactNode, title: string) => {
    setZoomElement({
      content: chart,
      title
    });
  };

  // 关闭放大视图
  const handleCloseZoom = () => {
    setZoomElement(null);
  };

  if (loading) {
    return (
      <div className={styles.loadingContainer}>
        {/* 可以添加加载动画 */}
        <p>{t('loading')}</p>
      </div>
    );
  }

  return (
    <div className={styles.dashboardContainer}> {/* 主容器样式匹配 */}
      {notificationContext}
      
      {/* 侧边栏 */}
      <Sidebar 
        open={sidebarOpen} 
        onToggle={() => setSidebarOpen(!sidebarOpen)} 
      />
      
      {/* 主内容区 */}
      <main className={styles.mainContent}>
        <header>
          <button 
            onClick={() => setSidebarOpen(!sidebarOpen)}
            aria-label={sidebarOpen ? t('menu.close') : t('menu.open')}
          >
            ☰
          </button>
          <h1 className={styles.pageTitle}>{t('admin.dashboard.title')}</h1> {/* 标题样式匹配 */}
          {selectedRegion && (
            <div className={styles.selectedRegionBadge}>
              {regionData.find(r => r.id === selectedRegion)?.name[i18n.language]}
              <button 
                onClick={() => setSelectedRegion(null)}
                aria-label={t('region.clearSelection')}
              >
                ×
              </button>
            </div>
          )}
        </header>

        {/* 统计卡片区域 - 使用网格布局 */}
        <section className={styles.statsGrid}> {/* 统计卡片网格样式 */}
          <StatisticCard 
            title={t('admin.stats.totalApplications')}
            value={statisticData?.totalApplications || 0}
            icon="file-text-o"
            color="#3498db"
            trend={statisticData?.totalApplications || 0 > 100 ? 'up' : 'down'}
          />
          <StatisticCard 
            title={t('admin.stats.pending')}
            value={statisticData?.pendingApplications || 0}
            icon="clock-o"
            color="#f39c12"
            trend={statisticData?.pendingApplications || 0 > 50 ? 'up' : 'down'}
          />
          <StatisticCard 
            title={t('admin.stats.approved')}
            value={statisticData?.approvedApplications || 0}
            icon="check-circle-o"
            color="#2ecc71"
            trend={statisticData?.approvedApplications || 0 > 70 ? 'up' : 'down'}
          />
          <StatisticCard 
            title={t('admin.stats.totalSales')}
            value={`¥${(statisticData?.totalSales || 0).toLocaleString()}`}
            icon="rmb"
            color="#9b59b6"
            trend={statisticData?.totalSales || 0 > 1000000 ? 'up' : 'down'}
          />
        </section>

        {/* 3D区域模型 */}
        <section>
          <h2 className={styles.chartTitle}>{t('admin.regionSales')}</h2> {/* 图表标题样式 */}
          <div className={styles.threeDChartContainer}> {/* 3D图表容器样式 */}
            <Canvas camera={{ position: [10, 10, 10] }}>
              <Environment preset="city" />
              <OrbitControls enableZoom={true} enablePan={true} />
              <ambientLight intensity={0.5} />
              <directionalLight position={[10, 10, 5]} intensity={1} />
              <RegionModel 
                regions={regionData}
                selectedRegion={selectedRegion}
                onSelectRegion={handleRegionSelect}
              />
            </Canvas>
          </div>
        </section>

        {/* 3D图表区域 - 使用网格布局 */}
        <section className={styles.chartsGrid}> {/* 图表网格样式 */}
          {charts.map((chart, index) => (
            <div key={index} className={styles.chartCard}> {/* 图表卡片样式 */}
              <ZoomableContainer 
                onZoom={() => handleChartZoom(
                  <ThreeDChart 
                    chart={chart} 
                    isZoomed={true} 
                  />,
                  chart.title[i18n.language]
                )}
                title={chart.title[i18n.language]}
              >
                <h3 className={styles.chartTitle}>{chart.title[i18n.language]}</h3>
                <ThreeDChart chart={chart} />
              </ZoomableContainer>
            </div>
          ))}
        </section>

        {/* 客户表格区域 */}
        <section className={styles.customerListSection}> {/* 客户列表样式 */}
          <ZoomableContainer 
            onZoom={() => handleChartZoom(
              <CustomerTable isZoomed={true} />,
              t('admin.table.title')
            )}
            title={t('admin.table.title')}
          >
            <h3 className={styles.chartTitle}>{t('admin.table.title')}</h3>
            <CustomerTable />
          </ZoomableContainer>
        </section>

        {/* 3D功能图标区域 - 使用按钮组样式 */}
        <section className={styles.buttonGroup}> {/* 按钮组样式 */}
          <ThreeDIcon 
            name={t('admin.functions.collection')}
            icon="hand-paper-o"
            color="#e74c3c"
            onClick={() => notificationApi.info({
              message: t('notification功能提示'),
              description: t('admin.functions.collectionDesc'),
            })}
          />
          <ThreeDIcon 
            name={t('admin.functions.carSelection')}
            icon="car"
            color="#3498db"
            onClick={() => notificationApi.info({
              message: t('notification功能提示'),
              description: t('admin.functions.carSelectionDesc'),
            })}
          />
          <ThreeDIcon 
            name={t('admin.functions.crm')}
            icon="users"
            color="#2ecc71"
            onClick={() => notificationApi.info({
              message: t('notification功能提示'),
              description: t('admin.functions.crmDesc'),
            })}
          />
          <ThreeDIcon 
            name={t('admin.functions.fraud')}
            icon="shield"
            color="#f39c12"
            onClick={() => notificationApi.info({
              message: t('notification功能提示'),
              description: t('admin.functions.fraudDesc'),
            })}
          />
          <ThreeDIcon 
            name={t('admin.functions.analysis')}
            icon="line-chart"
            color="#9b59b6"
            onClick={() => notificationApi.info({
              message: t('notification功能提示'),
              description: t('admin.functions.analysisDesc'),
            })}
          />
          <ThreeDIcon 
            name={t('admin.functions.settings')}
            icon="cog"
            color="#1abc9c"
            onClick={() => notificationApi.info({
              message: t('notification功能提示'),
              description: t('admin.functions.settingsDesc'),
            })}
          />
        </section>
      </main>

      {/* 聊天机器人 */}
      <Chatbot />

      {/* 放大视图 */}
      {zoomElement && (
        <div className={styles.zoomOverlay}>
          <div className={styles.zoomHeader}>
            <h2>{zoomElement.title}</h2>
            <button 
              className={styles.closeZoom} 
              onClick={handleCloseZoom}
              aria-label={t('zoom.close')}
            >
              ×
            </button>
          </div>
          <div className={styles.zoomContent}>
            {zoomElement.content}
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;